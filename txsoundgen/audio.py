from txsoundgen.utils import wave_write


class TXSoundData:
    """
    A class to encapsulate audio data and its properties.

    Args:
        data (bytes):
            The raw audio byte data.
        sample_rate (int, optional):
            The sample rate of the audio data. Defaults to 16000 Hz.
        sample_width (int, optional):
            The sample width in bytes. Defaults to 2 bytes (16-bit audio).
        sample_channels (int, optional):
            The number of audio channels. Defaults to 1 (mono).
    """

    def __init__(self, data, sample_rate=16000, sample_width=2, sample_channels=1):
        self.data = data
        self.sample_rate = sample_rate
        self.sample_width = sample_width
        self.sample_channels = sample_channels

    def write_wav(self, file: str):
        """
        Writes the audio data to a WAVE file.

        Args:
            file (string/file-like object): File path to write audio data to.
        Returns:
            string/file-like object: The file path or file-like object written to.
        """
        return wave_write(
            file,
            self.data,
            sample_width=self.sample_width,
            sample_channels=self.sample_channels,
            sample_rate=self.sample_rate,
        )
