"""Tests relating to `txsoundgen.model.Pack`."""
import os
import pytest

import txsoundgen.model

# pylint: disable=protected-access

@pytest.fixture(name="pack")
def fixture_pack():
    """Valid Pack object."""
    return txsoundgen.model.Pack({})


@pytest.fixture(name="soundlist")
def fixture_soundlist(pack):
    """Pack list"""
    original = {"system": {"valid": "string"}, "extra": {"converted": "string"}}
    return pack._convert_list(original)


def test_generate(pack):
    """Given a Sound object and configuration, a sound file is generated."""
    file = "test_pack_generate.wav"
    obj = txsoundgen.model.Sound("test")
    pack._process(file, obj)
    assert os.path.exists(file) is True
    os.remove(file)


def test_format_too_many_characters(pack):
    """A filename with too many characters is shortened."""
    assert pack._format_filename("toolong") == "toolon"


def test_format_invalid_characters(pack):
    """A filename with invalid characters has them removed."""
    assert pack._format_filename("@weirdchar") == "weirdc"


def test_format_file_extension(pack):
    """A filename with an extension has it stripped."""
    assert pack._format_filename("filext.wav") == "filext"


def test_format_whitespace(pack):
    """A filename with whitespace has it stripped."""
    assert pack._format_filename("spa ce") == "space"


def test_format_good_filenames(pack):
    """Given a set of good filenames, they stay the same."""
    errors = []
    good = ["1", "test", "valid-"]
    for string in good:
        if pack._format_filename(string) != string:
            errors.append(string)
    assert not errors, f"Incorrect response for {','.join(errors)}"


def test_converted_list_contains_correct_types(soundlist):
    """Given a dictionary of sound groups, the content is converted correctly."""
    errors = []
    if not "valid" in soundlist["SYSTEM"]:
        errors.append("Valid key")
    if not "conver" in soundlist["extra"]:
        errors.append("Converted key")
    if "conver" in soundlist["extra"] and not isinstance(
        soundlist["extra"]["conver"], txsoundgen.model.Sound
    ):  # Check contents are correct type.
        errors.append("Sound file")
    assert not errors, f"Incorrect response for {','.join(errors)}"

def test_soundlist_system_group(soundlist):
    """The 'SYSTEM' group exists in the soundlist and is uppercase."""
    if not "SYSTEM" in soundlist:
        assert False
