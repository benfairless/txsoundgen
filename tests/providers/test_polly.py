import pytest
import txsoundgen.audio
import txsoundgen.providers
import boto3, botocore.client
import botocore.exceptions


@pytest.fixture
def client():
    return txsoundgen.providers.Polly()


class TestPollySession:
    def test_polly_invalid_session(self):
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

    def test_polly_valid_session(self):
        """Given valid AWS credentials, a Polly client is created successfully."""
        assert isinstance(
            txsoundgen.providers.Polly(), txsoundgen.providers.Polly
        ), "Polly client was not created successfully."


class TestPolly:
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
