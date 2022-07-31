"""Tests relating to txsoundgen.utils."""
import txsoundgen.utils


class TestMergeConfig:
    """Tests relating to `txsoundgen.utils.merge_config()`."""

    def test_empty(self):
        """Given an empty configuration, returns the default configuration."""
        assert txsoundgen.utils.merge_config() == txsoundgen.utils.default_config

    def test_merge(self):
        """Given a valid configuration, returns a merged configuration."""
        assert (
            txsoundgen.utils.merge_config({"language": "en-US"})
            != txsoundgen.utils.default_config
        )
