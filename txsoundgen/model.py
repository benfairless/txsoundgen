"""
Sub-module containing objects for the storage, retrieval, and generation of text-to-speech data.

If you are working with txsoundgen programmatically this is probably the main submodule
you would be interested in interacting with.

Contents:
    - `CachedSound` - Store and retrieve cached audio data.
    - `Sound` - Generate WAVE-encoded audio data and store it to file, or use cached data.
    - `Pack` - Voice pack interface, for the creation of multiple sound files as a 'voice pack'.
"""
import os
import pathlib
import logging
import re

import peewee
import boto3

import txsoundgen.audio
import txsoundgen.utils

logger = logging.getLogger(__name__)


db = peewee.SqliteDatabase(None)
"""Database instance used for `CachedSound`.

See the
[peewee documentation](http://docs.peewee-orm.com/en/latest/peewee/database.html#using-sqlite)
for more details.
"""


class CachedSound(peewee.Model):
    """Store and retrieve cached audio data.

    Rather than requesting identical audio data numerous times (when processing multiple
    soundpacks for example), a database is used to store entries for each unique sound
    file generated. This massively improves processing speed and can significantly
    reduce the cost of pay-per-request Text-to-Speech engines.

    This class inherits from
    [`peewee.Model`](http://docs.peewee-orm.com/en/latest/peewee/models.html).
    """

    engine = peewee.CharField(default=txsoundgen.utils.default_config["engine"])
    """Engine used by text-to-speech service to synthesise speech."""
    language = peewee.CharField(default=txsoundgen.utils.default_config["language"])
    """Specifies the language code used by the speech engine, useful if using a bi-lingual voice.

    See [DescribeVoices](https://docs.aws.amazon.com/polly/latest/dg/API_DescribeVoices.html).
    """
    voice = peewee.CharField(default=txsoundgen.utils.default_config["voice"])
    """Voice ID used for synthesis with text-to-speech engine.

    For Amazon Polly there are many
    [Available voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html).
    """
    service = peewee.CharField(default="Polly")
    """Text-to-speech service used to synthesise speech data.

    Not useful now but other services
    could potentially be added at a later date. Defaults to `Polly`.
    """
    phrase = peewee.TextField()
    """Phrase which has been synthesised into sound data."""
    data = peewee.BlobField(unique=True)
    """Byte data for WAVE-encoded audio file generated based on the phrase and generator config."""

    class Meta:
        """Used by to manage database metadata."""

        table_name = "sound"
        database = db


class Sound:
    """High-level interface for generating sound files from phrases.

    Has the ability to automatically cache previous requests and retrieve them to reduce
    calls to voice synthesiser engines.

    Example:
        ```python
        >>> import boto3
        >>> client = boto3.client('polly')
        >>> from txsoundgen.model import *
        >>> db.init(':memory:', pragmas = { 'journal_mode': 'wal' })
        >>> db.create_tables([CachedSound])
        >>> eg = Sound('Welcome to EdgeTX')
        >>> eg.process(client, 'welcome.wav')
        'welcome.wav'

        ```
    """

    def __init__(self, phrase: str, config: dict = None):
        """Initialises a `Sound` object.

        Args:
            phrase (str):
                The (optionally SSML-enabled) text phrase that should be synthesised.
            config (dict, optional):
                Configuration which is passed to the sound generation service.
                See `txsoundgen.audio.polly_process()`.
        """
        self.config = txsoundgen.utils.merge_config(config)
        self.phrase = phrase
        self.service = "Polly"
        self.data = None

    def __repr__(self):
        return self.phrase

    def render(self, client: object = None):
        """Generates audio data using `txsoundgen.audio.polly_process()`.

        Args:
            client (botocore.client.Polly):
                A boto3 client object for communicating with the Amazon Polly service.
        """
        self.data = txsoundgen.audio.polly_process(client, self.phrase)
        return self.data

    def check_cache(self):
        """Uses cached sound data if it is available.

        Checks to see if an identical Speech object exists in the database already, and
        if so, sets `self.data` with the audio data stored in the cache . This reduces
        calls to the cloud speech engine, speeding up processing and reducing costs.

        If no database is initialised this will always return `False`.

        Returns:
            bool: Whether or not the sound already exists within the database.
        """
        try:
            cache = CachedSound.get(
                engine=self.config["engine"],
                language=self.config["language"],
                voice=self.config["voice"],
                service=self.service,
                phrase=f"{self.phrase}",
            )
            logger.debug('Found existing data for "%s" in cache', self.phrase)
            self.data = cache.data
            return True
        except (peewee.DoesNotExist, peewee.InterfaceError):
            logger.debug('No existing data for "%s" in cache', self.phrase)
            return False

    def process(self, client: object, file: str):
        """Synthesise phrase and write the data to a WAVE-encoded audio file.

        If appropriate audio data already exists in the database cache, that will be
        used. Otherwise, audio data is generated by the text-to-speech generation
        service, and then written to both the cache, and to the specified output file.

        If no cache database is initialised a cache will not be used.

        Will append `.wav` to the filename unless already specified.

        Makes use of the `check_cache()` method and `txsoundgen.audio.wave_write()`.

        Args:
            client (botocore.client.Polly):
                A boto3 client object for communicating with the Amazon Polly service.
            file (string/file-like object): File path to write audio data to.

        Returns:
            str: File path audio was written to.
        """
        if isinstance(file, str):
            file = re.sub(
                r"(?<!\.wav)$", r".wav", file
            )  # Ensure file ends in '.wav' extension.
        if self.check_cache():
            logger.info('Using cached audio data for "%s"', self.phrase)
        else:
            self.render(client)
            logger.info('Audio data generated for "%s"', self.phrase)
            try:
                CachedSound.create(
                    engine=self.config["engine"],
                    language=self.config["language"],
                    voice=self.config["voice"],
                    service=self.service,
                    phrase=self.phrase,
                    data=self.data,
                )
                logger.info(
                    'Audio data for "%s" saved in cache for future use', self.phrase
                )
            except peewee.InterfaceError:
                logger.warning('Unable to cache audio data for "%s"', self.phrase)
        txsoundgen.audio.wave_write(file, self.data)
        logger.info("Audio data for \"%s\" written to '%s'", self.phrase, file)
        return file


class Pack:
    """Voice pack interface, for the creation of multiple sound files as a 'voice pack'."""

    # TODO: Add description attribute

    def __init__(self, config: dict = None):
        self.config = txsoundgen.utils.merge_config(config)
        self.client = boto3.client("polly")
        self.name = self._format_filename(self.config["name"], safe_length=32)
        self.list = self._convert_list(self.config.get("sounds", {}))

        prefix = "voicepacks"
        lang = re.sub(
            r"(?:-.*)", "", self.config["language"]
        )  # Strips localisation from language name.
        self.path = os.path.join(prefix, self.name)
        self.packpath = os.path.join(self.path, "SOUNDS", "language", lang)

    def _format_filename(self, name: str, safe_length: int = 6):
        """Formats filenames to ensure they are compatible with OpenTX/EdgeTX firmware.

        Strips any characters that are not alphanumeric, '_', or '-' and then reduces
        the string to a maximum of six characters to make sure it is compatible with
        EdgeTX / OpenTX requirements.

        Args:
            name (str): Incoming filename.
            safe_length(int): Maximum length filename is permitted to be.

        Returns:
            str: Formatted filename.
        """
        pattern = re.compile(r"[^a-z0-9_-]+")
        safe_name = pattern.sub("", name.lower())[0:safe_length]
        if safe_name != name:
            logger.warning(
                "The filename '%s' is not allowed. Changed to '%s'.", name, safe_name
            )
        return safe_name

    def _convert_list(self, sound_list: dict):
        """Converts dictionary into sound list containing valid `Sound` objects.

        Args:
            sound_list (dict):
                Dictionary of sound groups and sounds. This is expected to be formatted
                as `{'group': {'name': 'phrase'}}`.

        Returns:
            dict: A converted version of the dictionary containing `Sound` objects.
        """
        output = {}
        for group, content in sound_list.items():
            content_list = {}
            if group == "system":
                group = group.upper()  # "SYSTEM" directory is expected to be uppercase.
            for name, phrase in content.items():
                key = self._format_filename(name)
                content_list[key] = Sound(phrase, config=self.config)
            output[group] = content_list
        return output

    def _setup(self):
        """Creates directory structure for voicepack."""
        path = pathlib.Path(self.path)
        if not path.exists():
            path.mkdir(parents=True)
            logger.info("Created directory for '%s' voicepack in '%s'", self.name, self.path)
        pathlib.Path(self.packpath).mkdir(parents=True, exist_ok=True)
        for group, __ in self.list.items():
            if group == "extra":
                group = ""  # Extra sound files are stored in the base path.
            pathlib.Path(os.path.join(self.packpath, group)).mkdir(exist_ok=True)


    def _process(self, filename: str, sound: Sound):
        """Wrapper for `txsoundgen.model.sound.process()`.

        Args:
            filename (str): Filename to write sound data to.
            sound (txsoundgen.model.Sound): Sound object to process.
        """
        return sound.process(self.client, filename)


    def readme(self):
        """Returns a Markdown-formatted README.md file for the voicepack."""
        description = "This is my soundpack."
        includes_default = True
        doc = f"""
{self.name.capitalize()} soundpack
{"=" * (len(self.name) + 10)}

{description}

The following sounds are included{" (as well as the default sounds)" if includes_default else ""}:
"""
        return doc

    # def process(self):
    #     pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
    #     worklist = []
    #     worklist.append('ddd')
    #     for name, phrase in self.phrases.items():
    #         worklist.append(Sound(phrase, name, prefix=self.prefix, extension=self.extension))
    #     logger.debug(f"Processing {len(worklist)} items in soundpack '{self.name}'")
    #     # for item in worklist:
    #         # item.generate(self.self.generator)
    #     queue(self.generator, worklist)
