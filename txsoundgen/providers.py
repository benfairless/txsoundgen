"""Providers for text-to-speech synthesis."""

import json
import logging
from pathlib import Path
from urllib.request import urlopen

import boto3
import piper
import piper.download_voices

from txsoundgen.audio import TXSoundData

provider_config = {
    "piper": {"voice": "alan", "language": "en_GB", "install": "resources/piper"},
    "polly": {"voice": "Amy", "language": "en-GB", "engine": "standard"},
}

_logger = logging.getLogger(__name__)


class Provider:
    """Base class for TTS providers."""

    def __init__(self) -> None:
        """Initialize the Provider base class."""

    def process(self, text, voice=None, language=None) -> None:
        """Process text into speech using the specified voice and language."""
        raise NotImplementedError("Subclasses must implement this method.")


class Piper(Provider):
    """Piper text-to-speech service client.

    Args:
        install_dir (string, optional):
            Directory to install Piper voice models to. Defaults to 'resources/piper'.

    """

    def __init__(
        self,
        config=provider_config["piper"],
        install_dir="resources/piper",
    ) -> None:
        """Initialize the Piper TTS provider."""
        self._config = config
        self.install_dir = install_dir or self._config["install"]

    def process(self, text, voice=None, language=None) -> TXSoundData:
        """Generate speech data using Piper TTS service.

        Used to generate audio data from text phrases via Piper speech synthesis
        library. It submits a text string to Piper for speech synthesis and processes
        the response into byte data.

        Args:
            text (string):
                The text phrase that should be synthesised.
            language (string, optional):
                Not yet implemented.
            voice (string, optional):
                Not yet implemented.

        Returns:
            `txsoundgen.audio.TXSoundData`:
                A TXSoundData object containing the audio byte data and sample rate.

        """
        voice = voice or self._config["voice"]
        language = language or self._config["language"]

        # Download the voice model if not already available
        model_id = f"{language}-{voice}-medium"
        model_path = Path(f"{self.install_dir}/{model_id}.onnx")
        if not model_path.exists():
            self.download_voice(model_id)

        # Perform synthesis
        model = piper.PiperVoice.load(model_path)
        response = next(
            model.synthesize(
                text,
                piper.SynthesisConfig(
                    volume=1.0,
                    length_scale=1.0,
                    noise_scale=1.0,
                    noise_w_scale=1.0,
                    normalize_audio=False,
                ),
            ),
        )

        # Return the audio data as a TXSoundData object (16-bit PCM)
        _logger.info('Successfully completed synthesis of "%s".', text)
        return TXSoundData(response.audio_int16_bytes, rate=response.sample_rate)

    def download_voice(self, model_id) -> None:
        """Download a voice model for Piper TTS.

        Args:
            model_id (string):
                The ID of the voice to download.

        """
        _logger.debug('Ensuring voice model "%s" is available.', model_id)

        # Check if the model is available for download
        with urlopen(piper.download_voices.VOICES_JSON) as response:
            voices_dict = json.load(response)
        if model_id not in sorted(voices_dict.keys()):
            raise ValueError("Not available")

        # Download the voice model
        _logger.info('Downloading voice model "%s".', model_id)
        install_dir = Path(self.install_dir)
        install_dir.mkdir(parents=True, exist_ok=True)
        piper.download_voices.download_voice(model_id, download_dir=install_dir)


class Polly(Provider):
    """AWS Polly text-to-speech service client.

    Args:
        session (boto3.session.Session, optional):
            A boto3 session object. If not provided, a default session is created.

    """

    def __init__(
        self,
        session=None,
        config=provider_config["polly"],
    ) -> None:
        """Initialize the Polly TTS provider."""
        if session is None:
            session = boto3.session.Session()
        sts = session.client("sts")
        self._config = config
        caller = sts.get_caller_identity()
        _logger.info("Authenticated to AWS as '%s'.", caller["Arn"])
        self._client = session.client("polly")
        self._config = provider_config["polly"]

    def process(self, text, voice=None, language=None) -> TXSoundData:
        """Generate speech data using AWS Polly.

        Used to generate audio data from text phrases via the Amazon Polly speech
        synthesis service. It submits a text string to Polly for speech synthesis
        and processes the response into byte data.

        Text-to-speech is processed using Polly's supported Speech Synthesis Markup
        Language (SSML).

        *See [Supported SSML tags](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html).*

        Args:
            text (string):
                The (optionally SSML-enabled) text phrase that should be
                synthesised.
            language (string, optional):
                Specifies the language code, useful if using a bi-lingual voice. See
                [DescribeVoices](https://docs.aws.amazon.com/polly/latest/dg/API_DescribeVoices.html).
            voice (string, optional):
                Voice ID used for synthesis with Polly.
                See [Available voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html).
            engine (string, optional):
                Specifies the engine (`standard` or `neural`) for Polly to use.
            output_format (string, optional):
                Specifies the format of the output audio. Defaults to `pcm`.

        Returns:
            `txsoundgen.audio.TXSoundData`:
                A TXSoundData object containing the audio byte data and sample rate.

        """
        voice = voice or self._config["voice"]
        language = language or self._config["language"]
        engine = self._config["engine"]
        ssml = f'<speak>{text}<break strength="weak"/></speak>'
        sample_rate = 16000

        response = self._client.synthesize_speech(
            Text=ssml,
            VoiceId=voice,
            LanguageCode=language,
            Engine=engine,
            TextType="ssml",
            OutputFormat="pcm",
        )

        # Return the audio data as a TXSoundData object (16-bit PCM)
        _logger.info('Successfully completed synthesis of "%s".', text)
        return TXSoundData(response["AudioStream"].read(), rate=sample_rate)
