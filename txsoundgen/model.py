"""
This sub-module contains objects for the storage, retrieval, and generation of text-to-speech data.

Contents:
    - `CachedSound` - Store and retrive cached audio data.
    - `Sound` - Generate WAVE-encoded audio data and store it to file, or use cached data.
"""

import logging
import re
import peewee

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

    class Meta:  # pylint: disable=R0903
        """Used by to manage database metadata."""

        table_name = "sound"
        database = db


class Sound:
    """High-level interface for generating sound files from phrases.

    Has the ability to automatically cache previous requests and retrieve them to reduce
    calls to voice synthesiser engines.

    Example:
        >>> import boto3
        >>> client = boto3.client('polly')
        >>> from txsoundgen.model import *
        >>> db.init(':memory:', pragmas = { 'journal_mode': 'wal' })
        >>> db.create_tables([CachedSound])
        >>> eg = Sound('Welcome to EdgeTX')
        >>> eg.process(client, 'welcome.wav')
        'welcome.wav'

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
