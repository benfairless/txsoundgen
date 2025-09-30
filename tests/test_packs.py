"""Tests relating to txsoundgen.pack."""

import os
import pytest
from txsoundgen.pack import Pack
from txsoundgen.model import Sound


@pytest.fixture(name="pack")
def fixture_pack():
    """Valid Pack object."""
    return Pack({})


def test_pack_format_filename(pack):
    """Given a set of valid and invalid filenames, they are formatted correctly."""
    errors = []
    safe = ["1", "test", "valid-"]
    not_safe = [
        ("toolong", "toolon"),  # More than the maximum characters
        ("@weirdchar", "weirdc"),  # Contains a non-valid character
        ("filext.wav", "filext"),  # Contains a file extension
        ("spa ce", "space"),  # Contains whitespace
    ]
    for string in safe:
        if pack._format_filename(string) != string:  # pylint: disable=W0212
            errors.append(string)
    for string, expected in not_safe:
        if pack._format_filename(string) != expected:  # pylint: disable=W0212
            errors.append(string)
    assert not errors, f"Incorrect response for {','.join(errors)}"


def test_pack_convert_list(pack):
    """Given a dictionary of sound groups, they are converted correctly."""
    errors = []
    original = {"test": {"valid": "string", "converted": "string"}}
    converted = pack._convert_list(original)["test"]  # pylint: disable=W0212
    if not "valid" in converted:
        errors.append("Valid key")
    if not "conver" in converted:
        errors.append("Converted key")
    if "conver" in converted and not isinstance(converted["conver"], Sound):
        errors.append("oo")
    assert not errors, f"Incorrect response for {','.join(errors)}"


def test_pack_generate(pack):
    """Given a Sound object and configuration, a sound file is generated."""
    file = "test_pack_generate.wav"
    obj = Sound("test")
    pack._generate(file, obj)  # pylint: disable=W0212
    assert os.path.exists(file) is True
    os.remove(file)
