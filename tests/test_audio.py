"""Tests relating to txsoundgen.audio."""

import os
import magic
import pytest
from botocore.exceptions import BotoCoreError, ClientError
import txsoundgen.audio
from tests import fixture_client  # pylint: disable=W0611


def test_wave_write_valid_data():
    """Given valid byte data, it is written to disk as a WAVE-encoded file."""
    file = "test_wave_write.tmp"
    txsoundgen.audio.wave_write(file, b"00")
    mime = magic.Magic(mime=True)
    assert mime.from_file(file) == "audio/x-wav"
    os.remove(file)


def test_wave_write_invalid_data():
    """When given invalid data to write to file, an exception is thrown."""
    file = "test_wave_write_invalid_data.tmp"
    with pytest.raises(Exception):
        txsoundgen.audio.wave_write(file, "Not a byte object")
    os.remove(file)


def test_polly_process_valid_string(client):
    """Given a valid string, Polly is able to process the request."""
    assert isinstance(
        txsoundgen.audio.polly_process(client, "Test Polly Process is Valid"), bytes
    )


def test_polly_process_invalid_string(client):
    """Given an invalid string, an error is returned."""
    with pytest.raises((BotoCoreError, ClientError)):
        txsoundgen.audio.polly_process(client, "<ssml_invalid_tag>")
