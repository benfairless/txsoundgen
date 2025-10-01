"""Audio data handling and processing for EdgeTX/OpenTX radios.

This module provides classes for managing audio data specifically formatted for
EdgeTX and OpenTX radio transmitters. The TXSoundData class handles raw audio
byte data with proper sample rates, bit depths, and channel configurations
optimized for radio compatibility.

Example:
    Basic usage for creating and exporting audio data:

    >>> from txsoundgen.audio import TXSoundData
    >>> # Create audio data from raw bytes
    >>> audio = TXSoundData(
    ...     data=b'\\x00\\x01' * 8000,  # Raw PCM audio bytes
    ...     rate=16000,                 # 16kHz sample rate
    ...     width=2,                    # 16-bit audio
    ...     channels=1                  # Mono audio
    ... )
    >>> # Write to a WAV file
    >>> audio.write_wav('output.wav')
    'output.wav'
"""

import logging

from pydub import AudioSegment

_logger = logging.getLogger(__name__)


class TXSoundData:
    """Class to encapsulate audio data and its properties.

    This class wraps raw audio byte data along with metadata describing its format,
    making it easy to work with audio intended for EdgeTX/OpenTX radios. The default
    parameters (16kHz, 16-bit, mono) are specifically chosen for maximum compatibility
    with these radio systems.

    Attributes:
        data (bytes): The raw audio byte data in PCM format.
        rate (int): The sample rate in Hz (samples per second).
        width (int): The sample width in bytes (2 bytes = 16-bit audio).
        channels (int): The number of audio channels (1 = mono, 2 = stereo).

    Args:
        data (bytes):
            The raw audio byte data in PCM (Pulse Code Modulation) format.
        rate (int, optional):
            The sample rate of the audio data in Hz. Defaults to 16000 Hz,
            which is the standard for EdgeTX/OpenTX radios.
        width (int, optional):
            The sample width in bytes. Defaults to 2 bytes (16-bit audio),
            which provides good quality while maintaining small file sizes.
        channels (int, optional):
            The number of audio channels. Defaults to 1 (mono), which is
            standard for radio transmitter audio.

    Example:
        Create audio data from TTS synthesis output:

        >>> from txsoundgen.audio import TXSoundData
        >>> # Assuming you have raw PCM audio bytes from a TTS engine
        >>> audio_bytes = b'\\x00\\x01' * 16000  # 1 second of audio
        >>> audio = TXSoundData(audio_bytes)
        >>> print(f"Duration: {len(audio.data) / (audio.rate * audio.width * audio.channels)} seconds")
        Duration: 1.0 seconds

        Create custom audio data with different parameters:

        >>> # Higher sample rate for better quality
        >>> hq_audio = TXSoundData(
        ...     data=audio_bytes,
        ...     rate=22050,
        ...     width=2,
        ...     channels=1
        ... )
    """

    def __init__(self, data, rate=16000, width=2, channels=1) -> None:
        """Initialize a TXSoundData instance.

        Args:
            data (bytes): The raw audio byte data.
            rate (int, optional): Sample rate in Hz. Defaults to 16000.
            width (int, optional): Sample width in bytes. Defaults to 2.
            channels (int, optional): Number of audio channels. Defaults to 1.
        """
        self.data = data
        self.rate = rate
        self.width = width
        self.channels = channels

    def write_wav(self, file: str, output_rate=16000) -> str:
        """Write audio data to a WAV file optimized for EdgeTX/OpenTX radios.

        This method exports the audio data as a WAVE file with parameters specifically
        tailored for EdgeTX and OpenTX radio transmitters. The output is always mono-channel
        (single channel) audio at 16kHz, which ensures compatibility with all radio systems
        while keeping file sizes manageable.

        The method uses ffmpeg via the pydub library to perform the conversion, ensuring
        high-quality output with proper WAV formatting.

        Args:
            file (str or file-like object):
                The destination file path or file-like object where the WAV file will be
                written. If a string is provided, it should be a valid file path. Parent
                directories must exist.
            output_rate (int, optional):
                The sample rate to use for the output WAV file in Hz. Defaults to 16000 Hz,
                which is the standard for EdgeTX/OpenTX radios. While you can specify a
                different rate, 16000 Hz is recommended for maximum compatibility.

        Returns:
            str or file-like object: The same file path or file-like object that was passed
            in, allowing for method chaining if desired.

        Example:
            Basic usage - write to a file:

            >>> from txsoundgen.audio import TXSoundData
            >>> audio = TXSoundData(b'\\x00\\x01' * 16000)
            >>> audio.write_wav('my_sound.wav')
            'my_sound.wav'

            Write multiple files with different output rates:

            >>> audio = TXSoundData(b'\\x00\\x01' * 16000, rate=22050)
            >>> # Standard rate for radios
            >>> audio.write_wav('radio_sound.wav', output_rate=16000)
            'radio_sound.wav'
            >>> # Higher quality for testing
            >>> audio.write_wav('test_sound.wav', output_rate=22050)
            'test_sound.wav'

            Use with a file-like object:

            >>> from io import BytesIO
            >>> buffer = BytesIO()
            >>> audio = TXSoundData(b'\\x00\\x01' * 8000)
            >>> audio.write_wav(buffer)
            <_io.BytesIO object at 0x...>

        Note:
            This method requires ffmpeg to be installed on your system. The pydub library
            uses ffmpeg for the actual audio conversion process.
        """
        # Uses ffmpeg via pydub to write the WAV file
        # https://github.com/jiaaro/pydub/blob/master/API.markdown
        sound = AudioSegment(
            data=self.data,
            sample_width=self.width,
            frame_rate=self.rate,
            channels=self.channels,
        )
        sound.export(
            file,
            format="wav",
            bitrate="16k",
            parameters=["-ar", str(output_rate)],
        )
        _logger.debug('Wrote audio data to "%s"', str(file))
        return file
