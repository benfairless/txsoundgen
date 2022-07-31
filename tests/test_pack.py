"""Tests relating to `txsoundgen.model.Pack`."""
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


class TestPack:
    """Tests relating to `txsoundgen.model.Pack`."""

    def test_generate(self, pack, tmp_path):
        """Given a Sound object and configuration, a sound file is generated."""
        file = tmp_path.joinpath("test_pack_generate.wav")
        obj = txsoundgen.model.Sound("test")
        pack._process(str(file), obj)
        assert file.exists() is True

    class TestFormatFilename:
        """Tests relating to `txsoundgen.model.pack._format_filename()."""

        def test_too_many_characters(self, pack):
            """A filename with too many characters is shortened."""
            assert pack._format_filename("toolong") == "toolon"

        def test_invalid_characters(self, pack):
            """A filename with invalid characters has them removed."""
            assert pack._format_filename("@weirdchar") == "weirdc"

        def test_file_extension(self, pack):
            """A filename with an extension has it stripped."""
            assert pack._format_filename("filext.wav") == "filext"

        def test_whitespace(self, pack):
            """A filename with whitespace has it stripped."""
            assert pack._format_filename("spa ce") == "space"

        def test_good_filenames(self, pack):
            """Given a set of good filenames, they stay the same."""
            errors = []
            good = ["1", "test", "valid-"]
            for string in good:
                if pack._format_filename(string) != string:
                    errors.append(string)
            assert not errors, f"Incorrect response for {','.join(errors)}"

    class TestConvertList:
        """Tests relating to `txsoundgen.model.Pack._convert_list()`."""

        def test_types(self, soundlist):
            """All items in the soundlist should be `txsoundgen.model.Sound`."""
            errors = []
            for __, contents in soundlist.items():
                for name, obj in contents.items():
                    if not isinstance(obj, txsoundgen.model.Sound):
                        errors.append(name)
            assert not errors

        def test_system_group(self, soundlist):
            """The 'SYSTEM' group exists in the soundlist and is uppercase."""
            if not "SYSTEM" in soundlist:
                assert False
