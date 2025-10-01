import pytest
import txsoundgen.audio
import txsoundgen.providers
import boto3, botocore.client
import botocore.exceptions


class TestPiper:
    """Test suite for the Piper TTS provider."""

    @pytest.fixture
    def client(self):
        return txsoundgen.providers.Piper()

    @pytest.fixture
    def client_tmp(self, tmp_path):
        return txsoundgen.providers.Piper(install_dir=tmp_path)

    def test_piper_processes_valid_string(self, client):
        """Given a valid string, Piper is able to process the request."""
        assert isinstance(
            client.process("Test Piper Process is Valid"), txsoundgen.audio.TXSoundData
        ), "Audio data is not a valid TXSoundData object."

    def test_piper_on_fresh_install(self, tmp_path):
        """Given a fresh install with no voice models, Piper is able to download and process the request."""
        client = txsoundgen.providers.Piper(install_dir=tmp_path)
        assert isinstance(
            client.process("Test Piper Process on Fresh Install"),
            txsoundgen.audio.TXSoundData,
        ), "Audio data is not a valid TXSoundData object."

    def test_piper_downloads_voice_model(self, client_tmp):
        """Given a valid voice model ID, Piper downloads the voice model successfully."""
        model_id = "en_GB-alan-medium"
        model_path = client_tmp.install_dir / f"{model_id}.onnx"
        client_tmp.download_voice(model_id)
        assert model_path.exists(), "Voice model was not downloaded successfully."

    def test_piper_download_raises_invalid_string(self, client_tmp):
        """Given an invalid voice model ID, an error is raised."""
        model_id = "en_GB-invalid-medium"
        with pytest.raises(ValueError):
            client_tmp.download_voice(model_id)


class TestPolly:
    """Test suite for the Polly TTS provider"""

    @pytest.fixture
    def client(self):
        return txsoundgen.providers.Polly()

    def test_polly_with_invalid_session(self):
        """Given invalid AWS credentials, an error is raised."""
        session = boto3.session.Session(
            aws_access_key_id="invalid",
            aws_secret_access_key="invalid",
            aws_session_token="invalid",
        )
        with pytest.raises(
            (botocore.exceptions.NoCredentialsError, botocore.exceptions.ClientError)
        ):
            txsoundgen.providers.Polly(session=session)

    def test_polly_with_valid_session(self):
        """Given valid AWS credentials, a Polly client is created successfully."""
        assert isinstance(
            txsoundgen.providers.Polly(), txsoundgen.providers.Polly
        ), "Polly client was not created successfully."

    def test_polly_processes_valid_string(self, client):
        """Given a valid string, AWS Polly is able to process the request."""
        assert isinstance(
            client.process("Test Polly Process is Valid"), txsoundgen.audio.TXSoundData
        ), "Audio data is not a valid TXSoundData object."

    def test_polly_raises_invalid_string(self, client):
        """Given an invalid string, an error is raised."""
        with pytest.raises(
            (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError)
        ):
            client.process("<ssml_invalid_tag>")
