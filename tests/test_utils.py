import pytest
import txsoundgen.utils
import magic
import os


# TODO: Refactor tests to use fixtures for setup/teardown where appropriate.


class TestWaveWrite:
    def test_wave_write_valid_data(self):
        """Given valid byte data, it is written to disk as a WAVE-encoded file."""
        file = "test_wave_write.tmp"
        txsoundgen.utils.wave_write(file, b"00")
        mime = magic.Magic(mime=True)
        assert mime.from_file(file) == "audio/x-wav"
        os.remove(file)
