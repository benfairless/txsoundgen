import pytest
import txsoundgen.audio
import txsoundgen.providers


@pytest.fixture
def client():
    return txsoundgen.providers.Piper()


class TestPiper:
    def test_piper_processes_valid_string(self, client):
        """Given a valid string, Piper is able to process the request."""
        assert isinstance(
            client.process("Test Piper Process is Valid"), txsoundgen.audio.TXSoundData
        ), "Audio data is not a valid TXSoundData object."
