"""Tests relating to `txsoundgen.model.Sound`."""
import txsoundgen.model
from tests import fixture_client  # pylint: disable=W0611


class TestSound:
    """Tests relating to `txsoundgen.model.Sound`."""

    def test_render(self, client):
        """When the `render()` method is called, the .data object contains bytes."""
        test = txsoundgen.model.Sound("Test Sound Creation")
        test.render(client)
        assert isinstance(test.data, bytes)

    def test_phrase(self):
        """When the object is referenced, it is represented by the 'phrase' attribute"""
        test = txsoundgen.model.Sound("Test Phrase")
        assert repr(test) == "Test Phrase"

    def test_config_override(self):
        """Given a config dict, the config is merged correctly."""
        conf = {"language": "en-US"}
        test = txsoundgen.model.Sound("Test Sound Config Override", conf)
        assert test.config["voice"] == "Amy"
        assert test.config["language"] == "en-US"

    def test_process_path(self, client, tmp_path):
        """Given a filename without an appropriate extension, '.wav' is added to the filename."""
        badfile = str(tmp_path.joinpath("test_sound_process_path"))
        goodfile = badfile + ".wav"
        test = txsoundgen.model.Sound("Test Sound Process")
        assert test.process(client, badfile) == goodfile
