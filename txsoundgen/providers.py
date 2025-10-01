"""Text-to-speech providers for audio synthesis.

This module provides interfaces to various text-to-speech (TTS) engines for generating
audio content. Each provider class handles the specifics of interacting with a particular
TTS service, converting text strings into audio data suitable for EdgeTX/OpenTX radios.

Currently supported providers:
    - **Piper**: An open-source, offline TTS engine that runs locally
    - **Polly**: Amazon's cloud-based neural TTS service

All providers return audio data in a standardized format (16kHz, 16-bit, mono) optimized
for radio transmitter compatibility.

Example:
    Using the Piper provider for offline TTS:

    >>> from txsoundgen.providers import Piper
    >>> # Initialize the Piper TTS provider
    >>> piper = Piper(install_dir='./models')
    >>> # Generate speech from text
    >>> audio = piper.process("Hello world")
    >>> # Save to file
    >>> audio.write_wav('hello.wav')
    'hello.wav'

    Using the Polly provider for cloud-based TTS:

    >>> from txsoundgen.providers import Polly
    >>> # Initialize with AWS credentials via boto3
    >>> polly = Polly()
    >>> # Generate speech with SSML support
    >>> audio = polly.process("<emphasis>Hello</emphasis> world")
    >>> audio.write_wav('hello_polly.wav')
    'hello_polly.wav'
"""

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
    """Base class for TTS providers.

    This abstract base class defines the interface that all TTS provider implementations
    must follow. It ensures a consistent API across different TTS services, making it
    easy to switch between providers or support multiple providers in the same application.

    Subclasses must implement the `process` method to handle text-to-speech conversion
    for their specific TTS service.

    Example:
        Creating a custom provider:

        >>> from txsoundgen.providers import Provider
        >>> from txsoundgen.audio import TXSoundData
        >>> 
        >>> class CustomTTS(Provider):
        ...     def process(self, text, voice=None, language=None):
        ...         # Your custom TTS logic here
        ...         audio_bytes = your_tts_function(text)
        ...         return TXSoundData(audio_bytes)
    """

    def __init__(self) -> None:
        """Initialize the Provider base class."""

    def process(self, text, voice=None, language=None) -> None:
        """Process text into speech using the specified voice and language.

        This method must be implemented by all provider subclasses to convert
        text strings into synthesized speech audio.

        Args:
            text (str): The text to convert to speech.
            voice (str, optional): The voice ID or name to use for synthesis.
            language (str, optional): The language code for synthesis.

        Returns:
            TXSoundData: Audio data containing the synthesized speech.

        Raises:
            NotImplementedError: If the subclass doesn't implement this method.
        """
        raise NotImplementedError("Subclasses must implement this method.")


class Piper(Provider):
    """Piper text-to-speech service client.

    Piper is an open-source, fast, and local neural text-to-speech system. Unlike
    cloud-based services, Piper runs entirely on your machine, providing privacy,
    reliability, and no usage costs. It uses ONNX models for fast inference and
    supports multiple languages and voices.

    This class handles downloading voice models, managing the local installation,
    and performing speech synthesis using the Piper library.

    Attributes:
        install_dir (str): Path to the directory where Piper voice models are stored.

    Args:
        config (dict, optional):
            Configuration dictionary with default voice and language settings.
            If not provided, uses the default config with voice='alan' and
            language='en_GB'.
        install_dir (str, optional):
            Directory to install Piper voice models to. Defaults to 'resources/piper'.
            Voice models are automatically downloaded to this location when needed.

    Example:
        Basic usage with default settings:

        >>> from txsoundgen.providers import Piper
        >>> piper = Piper()
        >>> audio = piper.process("Battery low")
        >>> audio.write_wav('battery_low.wav')
        'battery_low.wav'

        Using a custom voice and language:

        >>> piper = Piper(
        ...     config={'voice': 'jenny', 'language': 'en_US'},
        ...     install_dir='./my_models'
        ... )
        >>> audio = piper.process("Telemetry lost")
        >>> audio.write_wav('telemetry.wav')
        'telemetry.wav'

        Specify voice at synthesis time:

        >>> piper = Piper()
        >>> # Use British English voice
        >>> audio_gb = piper.process("Hello", voice="alan", language="en_GB")
        >>> # Use American English voice
        >>> audio_us = piper.process("Hello", voice="jenny", language="en_US")

    Note:
        Voice models are downloaded automatically on first use. The download
        size varies by model but typically ranges from 10-50 MB per voice.
    """

    def __init__(
        self,
        config=provider_config["piper"],
        install_dir="resources/piper",
    ) -> None:
        """Initialize the Piper TTS provider.

        Args:
            config (dict, optional): Configuration with voice and language defaults.
            install_dir (str, optional): Directory for voice model storage.
        """
        self._config = config
        self.install_dir = install_dir or self._config["install"]

    def process(self, text, voice=None, language=None) -> TXSoundData:
        """Generate speech data using Piper TTS service.

        Converts text into synthesized speech using Piper's neural TTS models. This method
        handles model downloading if necessary, loads the appropriate voice model, performs
        synthesis with optimal settings, and returns the audio data in a format ready for
        use with EdgeTX/OpenTX radios.

        The synthesis process:
        1. Determines which voice model to use (from parameters or config)
        2. Downloads the voice model if not already present
        3. Loads the model and performs neural TTS synthesis
        4. Returns 16-bit PCM audio data at the model's native sample rate

        Args:
            text (str):
                The text phrase to synthesize into speech. Plain text is recommended,
                though Piper has limited SSML support in some models.
            voice (str, optional):
                Voice name to use (e.g., 'alan', 'jenny', 'danny'). If not provided,
                uses the default voice from the config. Available voices depend on
                the selected language.
            language (str, optional):
                Language code in the format 'en_GB', 'en_US', 'de_DE', etc. If not
                provided, uses the default language from the config. Must match an
                available Piper language/voice combination.

        Returns:
            TXSoundData: An audio data object containing the synthesized speech as
            16-bit PCM data at the model's native sample rate (typically 16000 or 22050 Hz).

        Example:
            Simple text-to-speech:

            >>> from txsoundgen.providers import Piper
            >>> piper = Piper()
            >>> audio = piper.process("Battery low")
            >>> print(f"Sample rate: {audio.rate} Hz")
            Sample rate: 22050 Hz

            Generate multiple phrases with the same provider:

            >>> piper = Piper()
            >>> phrases = ["Timer 1 elapsed", "Signal lost", "Throttle warning"]
            >>> for i, phrase in enumerate(phrases):
            ...     audio = piper.process(phrase)
            ...     audio.write_wav(f"phrase_{i}.wav")

            Use different voices for different phrases:

            >>> piper = Piper()
            >>> # Male voice
            >>> audio1 = piper.process("System armed", voice="alan", language="en_GB")
            >>> # Female voice  
            >>> audio2 = piper.process("All checks complete", voice="jenny", language="en_US")

        Note:
            Voice models are cached in the install_dir after first download, so
            subsequent calls with the same voice are much faster.
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

        Fetches a specific voice model from the Piper voice repository and installs
        it to the configured install directory. Voice models are ONNX format neural
        networks optimized for fast inference.

        The method first verifies that the requested model exists in the Piper voice
        repository before attempting to download it. If the model is already present
        in the install directory, this method can be safely called again (it won't
        re-download).

        Args:
            model_id (str):
                The full model identifier in the format 'language-voice-quality',
                for example 'en_GB-alan-medium' or 'en_US-jenny-low'. The quality
                levels are typically 'low', 'medium', or 'high', with higher quality
                models being larger but producing better audio.

        Raises:
            ValueError: If the specified model_id is not available in the Piper
                voice repository.

        Example:
            Download a specific voice model:

            >>> from txsoundgen.providers import Piper
            >>> piper = Piper(install_dir='./models')
            >>> # Download British English male voice
            >>> piper.download_voice('en_GB-alan-medium')
            >>> # Download American English female voice
            >>> piper.download_voice('en_US-jenny-medium')

            Pre-download multiple voices:

            >>> piper = Piper()
            >>> voices = ['en_GB-alan-medium', 'en_US-jenny-low', 'de_DE-thorsten-medium']
            >>> for voice in voices:
            ...     try:
            ...         piper.download_voice(voice)
            ...         print(f"Downloaded {voice}")
            ...     except ValueError:
            ...         print(f"Voice {voice} not available")

        Note:
            Voice model files are typically 10-50 MB depending on quality level.
            Download time will vary based on your internet connection speed.
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

    Amazon Polly is a cloud-based neural text-to-speech service that converts text into
    lifelike speech. It offers a variety of natural-sounding voices across multiple
    languages and supports advanced features like Speech Synthesis Markup Language (SSML)
    for fine-grained control over pronunciation, emphasis, and pacing.

    This class handles authentication with AWS, manages API calls to Polly, and processes
    the returned audio stream into a format suitable for EdgeTX/OpenTX radios.

    Attributes:
        _client: The boto3 Polly client used for API calls.
        _config (dict): Configuration dictionary with default voice, language, and engine settings.

    Args:
        session (boto3.session.Session, optional):
            A boto3 session object with AWS credentials configured. If not provided,
            a default session is created, which will use credentials from environment
            variables, AWS config files, or IAM roles. See boto3 documentation for
            credential configuration options.
        config (dict, optional):
            Configuration dictionary with default settings. If not provided, uses the
            default config with voice='Amy', language='en-GB', and engine='standard'.

    Example:
        Basic usage with default AWS credentials:

        >>> from txsoundgen.providers import Polly
        >>> polly = Polly()
        >>> audio = polly.process("Transmitter ready")
        >>> audio.write_wav('ready.wav')
        'ready.wav'

        Use with explicit AWS session:

        >>> import boto3
        >>> session = boto3.Session(
        ...     aws_access_key_id='YOUR_KEY',
        ...     aws_secret_access_key='YOUR_SECRET',
        ...     region_name='us-east-1'
        ... )
        >>> polly = Polly(session=session)
        >>> audio = polly.process("Hello world")

        Use SSML for advanced control:

        >>> polly = Polly()
        >>> # Add emphasis and pauses
        >>> text = '<emphasis level="strong">Warning</emphasis><break time="500ms"/>Low fuel'
        >>> audio = polly.process(text)
        >>> audio.write_wav('warning.wav')

        Generate speech in different voices:

        >>> polly = Polly()
        >>> # British female voice
        >>> audio1 = polly.process("System check", voice="Amy", language="en-GB")
        >>> # American male voice
        >>> audio2 = polly.process("System check", voice="Matthew", language="en-US")
        >>> # Australian female voice
        >>> audio3 = polly.process("System check", voice="Nicole", language="en-AU")

    Note:
        - AWS credentials must be configured for this provider to work
        - API calls to Polly incur costs based on character count
        - Neural voices generally sound more natural than standard voices but cost more
        - See AWS Polly documentation for available voices and pricing

    Raises:
        ClientError: If AWS authentication fails or the API request is invalid.
    """

    def __init__(
        self,
        session=None,
        config=provider_config["polly"],
    ) -> None:
        """Initialize the Polly TTS provider.

        Args:
            session (boto3.session.Session, optional): AWS session with credentials.
            config (dict, optional): Configuration dictionary with defaults.
        """
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

        Converts text into high-quality synthesized speech using Amazon Polly's neural
        or standard TTS engines. The text is automatically wrapped in SSML (Speech
        Synthesis Markup Language) tags to ensure proper phrasing and spacing.

        This method handles the complete workflow: preparing the SSML text, making the
        API call to Polly, streaming the audio response, and packaging it into a
        TXSoundData object with the appropriate format for radio use.

        Text-to-speech is processed using Polly's Speech Synthesis Markup Language (SSML)
        support, which allows for advanced control over speech output including emphasis,
        pauses, pronunciation, and more.

        *See [Supported SSML tags](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html)
        for details on available SSML features.*

        Args:
            text (str):
                The text phrase to synthesize. Can be plain text or include SSML tags
                for advanced control (tags like <emphasis>, <break>, <prosody>, etc.).
                The text is automatically wrapped in <speak> tags with a weak break at
                the end for natural phrasing.
            voice (str, optional):
                Voice ID to use for synthesis (e.g., 'Amy', 'Matthew', 'Joanna').
                If not provided, uses the voice from the config. Different voices
                have different characteristics and language support.
                See [Available voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html).
            language (str, optional):
                Language code in BCP-47 format (e.g., 'en-GB', 'en-US', 'de-DE').
                This is particularly useful for bilingual voices or to ensure proper
                pronunciation. If not provided, uses the language from config.
                See [DescribeVoices API](https://docs.aws.amazon.com/polly/latest/dg/API_DescribeVoices.html).

        Returns:
            TXSoundData: Audio data object containing the synthesized speech as 16-bit
            PCM data at 16000 Hz, ready for use with EdgeTX/OpenTX radios.

        Example:
            Simple text-to-speech:

            >>> from txsoundgen.providers import Polly
            >>> polly = Polly()
            >>> audio = polly.process("Radio check")
            >>> audio.write_wav('radio_check.wav')
            'radio_check.wav'

            Use SSML for natural pauses:

            >>> polly = Polly()
            >>> text = "Battery at <break time='200ms'/> 50 percent"
            >>> audio = polly.process(text)

            Control speech rate and volume with SSML prosody:

            >>> polly = Polly()
            >>> text = '<prosody rate="slow" volume="loud">Warning</prosody> Low altitude'
            >>> audio = polly.process(text)

            Generate announcements in multiple voices:

            >>> polly = Polly()
            >>> # British female voice
            >>> audio_amy = polly.process("Ready to fly", voice="Amy", language="en-GB")
            >>> # American male voice
            >>> audio_matthew = polly.process("Ready to fly", voice="Matthew", language="en-US")
            >>> # Australian female voice
            >>> audio_nicole = polly.process("Ready to fly", voice="Nicole", language="en-AU")

            Batch process multiple phrases:

            >>> polly = Polly()
            >>> phrases = {
            ...     "armed": "System armed",
            ...     "disarmed": "System disarmed",
            ...     "battery": "Battery low",
            ...     "signal": "Signal lost"
            ... }
            >>> for name, text in phrases.items():
            ...     audio = polly.process(text)
            ...     audio.write_wav(f"{name}.wav")

        Note:
            - Each API call to Polly incurs a cost based on the number of characters
            - Standard voices cost less than neural voices but may sound less natural
            - The engine type (standard/neural) is set in the config, not per-call
            - Audio is always returned as 16kHz, 16-bit mono PCM for radio compatibility

        Raises:
            botocore.exceptions.ClientError: If the AWS API call fails due to
                authentication issues, invalid parameters, or service errors.
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
