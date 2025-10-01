"""Tests for the TTS provider classes."""

import boto3
import botocore.exceptions
import pytest

import txsoundgen.audio
import txsoundgen.providers


class TestProvider:
    """Test suite for the base Provider class."""

    def test_provider_raises_invalid_string(self) -> None:
        """Given an invalid provider name, an error is raised."""
        provider = txsoundgen.providers.Provider()
        with pytest.raises(NotImplementedError):
            provider.process("Test Provider is Invalid")


class TestPiper:
    """Test suite for the Piper TTS provider."""

    @pytest.fixture
    def client(self) -> txsoundgen.providers.Piper:
        """Return a Piper client instance."""
        return txsoundgen.providers.Piper()

    @pytest.fixture
    def client_tmp(self, tmp_path) -> txsoundgen.providers.Piper:
        """Return a Piper client instance with a temporary install directory."""
        return txsoundgen.providers.Piper(install_dir=tmp_path)

    def test_piper_processes_valid_string(self, client) -> None:
        """Given a valid string, Piper is able to process the request."""
        assert isinstance(
            client.process("Test Piper Process is Valid"),
            txsoundgen.audio.TXSoundData,
        ), "Audio data is not a valid TXSoundData object."

    @pytest.mark.slow
    def test_piper_on_fresh_install(self, tmp_path) -> None:
        """Given a fresh install, Piper downloads model and processes the request."""
        client = txsoundgen.providers.Piper(install_dir=tmp_path)
        assert isinstance(
            client.process("Test Piper Process on Fresh Install"),
            txsoundgen.audio.TXSoundData,
        ), "Audio data is not a valid TXSoundData object."

    @pytest.mark.slow
    def test_piper_downloads_voice_model(self, client_tmp) -> None:
        """Given a valid voice model ID, Piper downloads voice model successfully."""
        model_id = "en_GB-alan-medium"
        model_path = client_tmp.install_dir / f"{model_id}.onnx"
        client_tmp.download_voice(model_id)
        assert model_path.exists(), "Voice model was not downloaded successfully."

    def test_piper_download_raises_invalid_string(self, client_tmp) -> None:
        """Given an invalid voice model ID, an error is raised."""
        model_id = "en_GB-invalid-medium"
        with pytest.raises(ValueError, match="Not available"):
            client_tmp.download_voice(model_id)


class TestPolly:
    """Test suite for the Polly TTS provider"""

    @pytest.fixture
    def client(self) -> txsoundgen.providers.Polly:
        """Return a Polly client instance."""
        return txsoundgen.providers.Polly()

    def test_polly_with_invalid_session(self) -> None:
        """Given invalid AWS credentials, an error is raised."""
        session = boto3.session.Session(
            aws_access_key_id="invalid",
            aws_secret_access_key="invalid",
            aws_session_token="invalid",
        )
        with pytest.raises(
            (botocore.exceptions.NoCredentialsError, botocore.exceptions.ClientError),
        ):
            txsoundgen.providers.Polly(session=session)

    def test_polly_with_valid_session(self) -> None:
        """Given valid AWS credentials, a Polly client is created successfully."""
        assert isinstance(txsoundgen.providers.Polly(), txsoundgen.providers.Polly), (
            "Polly client was not created successfully."
        )

    def test_polly_processes_valid_string(self, client) -> None:
        """Given a valid string, AWS Polly is able to process the request."""
        assert isinstance(
            client.process("Test Polly Process is Valid"),
            txsoundgen.audio.TXSoundData,
        ), "Audio data is not a valid TXSoundData object."

    def test_polly_raises_invalid_string(self, client) -> None:
        """Given an invalid string, an error is raised."""
        with pytest.raises(
            (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError),
        ):
            client.process("<ssml_invalid_tag>")
