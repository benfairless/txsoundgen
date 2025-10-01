"""Tests for audio classes."""

import magic
import pytest

import txsoundgen.audio

WAV_CONFIG = {
    "data": b"00",
    "rate": 16000,
    "width": 2,
    "channels": 1,
}


class TestTXSoundData:
    """Test suite for the TXSoundData class."""

    @pytest.fixture
    def audio_data(self) -> txsoundgen.audio.TXSoundData:
        """Return a sample TXSoundData object."""
        return txsoundgen.audio.TXSoundData(
            data=WAV_CONFIG["data"],
            rate=WAV_CONFIG["rate"],
            width=WAV_CONFIG["width"],
            channels=WAV_CONFIG["channels"],
        )

    @pytest.fixture
    def tmp_file(self, tmp_path) -> str:
        """Return a temporary file path for testing."""
        return tmp_path / "test_output.wav"

    def test_object_initialization(self, audio_data) -> None:
        """Given audio data, when initialized, then properties are set correctly."""
        assert audio_data.data == WAV_CONFIG["data"], "Data does not match."
        assert audio_data.rate == WAV_CONFIG["rate"], "Rate does not match."
        assert audio_data.width == WAV_CONFIG["width"], "Width does not match."
        assert audio_data.channels == WAV_CONFIG["channels"], "Channels does not match."

    def test_sound_data_is_valid(self, audio_data, tmp_file) -> None:
        """Given audio data, when written to a WAV file, then the file is valid."""
        audio_data.write_wav(tmp_file)
        assert tmp_file.exists(), "WAV file was not created successfully."
        mime = magic.Magic(mime=True)
        assert mime.from_file(tmp_file) == "audio/x-wav", "WAV file is not valid."
