"""Tests used by PyTest to ensure the module is working as expected."""

import os
import sys
import boto3
import pytest


# Modifies path to allow importing of module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(name="client")
def fixture_client():
    """Boto3 Polly client used for AWS calls."""
    return boto3.client("polly")
