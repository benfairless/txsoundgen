"""Tests relating to txsoundgen.model."""

import os

# import pytest
import txsoundgen.model
from tests import fixture_client  # pylint: disable=W0611


def test_sound_creation(client):
    """When the sound.render method is called, the object has a .data attribute containing bytes."""
    test = txsoundgen.model.Sound("Test Sound Creation")
    test.render(client)
    assert isinstance(test.data, bytes)


def test_sound_config_override():
    """Given a config dict, the config is merged correctly."""
    conf = {"language": "en-US"}
    test = txsoundgen.model.Sound("Test Sound Config Override", conf)
    assert test.config["voice"] == "Amy"
    assert test.config["language"] == "en-US"


def test_sound_process_path(client):
    """Given a filename without an appropriate extension, '.wav' is added to the filename."""
    badfile = "test_sound_process_path"
    goodfile = badfile + ".wav"
    test = txsoundgen.model.Sound("Test Sound Process")
    assert test.process(client, badfile) == goodfile
    os.remove(goodfile)
