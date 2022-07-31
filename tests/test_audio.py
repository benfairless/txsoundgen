"""Tests relating to txsoundgen.audio."""
import magic
import pytest
from botocore.exceptions import BotoCoreError, ClientError

import txsoundgen.audio
from tests import fixture_client  # pylint: disable=unused-import


class TestWaveWrite:
    """Tests relating to `txsoundgen.audio.wave_write()`."""

    def test_valid_data(self, tmp_path):
        """Given valid byte data, it is written to disk as a WAVE-encoded file."""
        file = tmp_path.joinpath("test_valid_data.wav")
        txsoundgen.audio.wave_write(str(file), b"00")
        mime = magic.Magic(mime=True)
        assert mime.from_file(file) == "audio/x-wav"

    def test_invalid_data(self, tmp_path):
        """When given invalid data to write to file, an exception is thrown."""
        file = str(tmp_path.joinpath("test_wave_write_invalid_data.tmp"))
        with pytest.raises(Exception):
            txsoundgen.audio.wave_write(file, "Not a byte object")


class TestPollyProcess:
    """Tests relating to `txsoundgen.audio.polly_process()."""

    def test_valid_string(self, client):
        """Given a valid string, Polly is able to process the request."""
        assert isinstance(
            txsoundgen.audio.polly_process(client, "Test Polly Process is Valid"), bytes
        )

    def test_invalid_string(self, client):
        """Given an invalid string, an error is returned."""
        with pytest.raises((BotoCoreError, ClientError)):
            txsoundgen.audio.polly_process(client, "<ssml_invalid_tag>")
