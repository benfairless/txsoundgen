"""Sub-module containing low level functions for the creation and processing of audio data directly.

Contents:
    - `polly_process()` - Manage generation and processing of text-to-speech via Amazon Polly.
    - `wave_write()` - Writes WAVE-encoded audio data to a file path, or file-like object.
"""
import logging
import wave
from contextlib import closing
from botocore.exceptions import BotoCoreError, ClientError

import txsoundgen.utils


logger = logging.getLogger(__name__)


def polly_process(client: object, phrase: str, config: dict = None):
    """Manage generation and processing of text-to-speech via Amazon Polly.

    Used to generate WAVE-encoded 16kHz audio data from text phrases via the Amazon
    Polly speech synthesis service. It submits a text string to Polly for speech
    synthesis and processes the response into byte data.

    Text-to-speech is processed using Polly's supported Speech Synthesis Markup Language
    (SSML).

    *See [Supported SSML tags](https://docs.aws.amazon.com/polly/latest/dg/supportedtags.html).*

    Args:
        client (botocore.client.Polly):
            A boto3 client object for communicating with the Amazon Polly service.
        phrase (string):
            The (optionally SSML-enabled) text phrase that should be
            synthesised.
        config (dict, optional):
            Dictionary containting optional configuration parameters.

    Returns:
        A byte object containing the generated audio data.

    Raises:
        RunTimeError

    Configuration:
        The configuration dictionary can optionally contain any of the following keys.
        They are merged over the default configuration provided by `txsound.config`.

        - `engine`:
            Specifies the engine (`standard` or `neural`) for Polly to use.
            Defaults to `standard`.
        - `voice`:
            Voice ID used for synthesis with Polly.
            See [Available voices](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html).
        - `language`:
            Specifies the language code, useful if using a bi-lingual voice. See
            [DescribeVoices](https://docs.aws.amazon.com/polly/latest/dg/API_DescribeVoices.html).

    Example:
        ```python
        >>> import boto3
        >>> from txsoundgen.audio import polly_process
        >>> conf = {'voice': 'Amy', 'language': 'en-GB'}
        >>> gen = polly_process(boto3.client('polly'), 'Welcome to Edge TX', conf)#
        >>> type(gen)
        <class 'bytes'>

        ```
    """
    config = txsoundgen.utils.merge_config(config)
    ssml = f'<speak>{phrase}<break strength="weak"/></speak>'
    try:
        logger.debug('Requesting synthesis of "%s" from AWS Polly', phrase)
        response = client.synthesize_speech(
            Engine=config["engine"],
            LanguageCode=config["language"],
            SampleRate=str(16000),
            VoiceId=config["voice"],
            Text=ssml,
            TextType="ssml",
            OutputFormat="pcm",
        )
        logger.debug('Received response from AWS Polly for "%s"', phrase)
    except (BotoCoreError, ClientError) as error:
        logger.critical(error)
        raise error
    with closing(response["AudioStream"]) as stream:
        output = stream.read()
        logger.debug('Successfully completed synthesis of "%s"', phrase)
        return output


def wave_write(file: str, data: bytes):
    """Writes WAVE-encoded audio data to a file path, or file-like object.

    Creates mono-channel audio audio at 16kHz, which is what is supported by
    EdgeTX / OpenTX radios, and is output from audio generated by `polly_process()`.

    Args:
        file (string/file-like object): File path to write audio data to.
        data (bytes): Audio data to write.

    Raises:
        IOError

    Example:
        ```python
        >>> from txsoundgen.audio import wave_write
        >>> wave_write('test.wav', b'00')
        'test.wav'

        >>> import boto3
        >>> from txsoundgen.audio import polly_process, wave_write
        >>> gen = polly_process(boto3.client('polly'), 'Welcome to Edge TX')
        >>> wave_write('welcome.wav', gen)
        'welcome.wav'

        ```
        This would request a text-to-speech conversion of the phrase 'Welcome to Edge
        TX' from Amazon Polly and then write the sound data to a WAVE file called
        `welcome.wav`.
    """
    try:
        with wave.open(file, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(data)
        logger.debug('Wrote audio data to "%s"', str(file))
        return file
    except Exception as error:
        logger.error(error)
        raise error
