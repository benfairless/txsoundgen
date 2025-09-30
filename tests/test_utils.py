"""Tests relating to txsoundgen.utils."""

import txsoundgen.utils


def test_merge_config_empty():
    """Given an empty configuration, returns the default configuration."""
    assert txsoundgen.utils.merge_config() == txsoundgen.utils.default_config


def test_merge_config_merge():
    """Given a valid configuration, returns a merged configuration."""
    assert (
        txsoundgen.utils.merge_config({"language": "en-US"})
        != txsoundgen.utils.default_config
    )
