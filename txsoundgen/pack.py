import os
import pathlib
import logging
import re
import boto3

import txsoundgen.utils
import txsoundgen.model


logger = logging.getLogger(__name__)


class Pack:
    """Voice pack interface, for the creation of multiple sound files as a 'voice pack'."""

    # TODO: Automatically create README.md for voice pack
    # TODO: Add description attribute
    # TODO: Re-consider how to calculate path

    def __init__(self, conf: dict = None):
        self.config = txsoundgen.utils.merge_config(conf)
        self.client = boto3.client("polly")
        self.name = self.config["name"]
        self.list = self._convert_list(self.config.get("sounds", {}))

        # self.prefix = self.config.get('path', f'voicepacks/{self.name}/')
        # self.basepath = os.environ.get('VOICEPACK_DIR', '.') + '/'
        # self.path = self.basepath + self.prefix

    def _format_filename(self, name: str):
        """Formats filenames to ensure they are compatible with OpenTX/EdgeTX firmware.

        Strips any characters that are not alphanumeric, '_', or '-' and then reduces
        the string to a maximum of six characters to make sure it is compatible with
        EdgeTX / OpenTX requirements.

        Args:
            name (str): Incoming filename

        Returns:
            str: Formatted filename
        """
        safe_length = 6  # Firmware only supports filenames up to six characters.
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
            for name, phrase in content.items():
                key = self._format_filename(name)
                content_list[key] = txsoundgen.model.Sound(phrase, config=self.config)
            output[group] = content_list
        return output

    def _generate(self, filename: str, sound: txsoundgen.model.Sound):
        """Wrapper for `txsoundgen.model.sound.process()`.

        Args:
            filename (str): Filename to write sound data to.
            sound (txsoundgen.model.Sound): Sound object to process.
        """
        return sound.process(self.client, filename)

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
