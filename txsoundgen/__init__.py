"""TXSoundGen - Sound pack generator for EdgeTX/OpenTX radios.

.. include:: ../README.md

TXSoundGen is a Python library and toolset for generating custom voice packs for
EdgeTX and OpenTX radio transmitters. It supports multiple text-to-speech engines
and provides a flexible, programmable interface for creating comprehensive sound
packs tailored to your needs.

Key Features:
    - **Multiple TTS Providers**: Support for both local (Piper) and cloud-based (AWS Polly) TTS
    - **Radio-Optimized Audio**: Generates 16kHz mono WAV files for maximum compatibility
    - **Flexible Configuration**: Programmatic API and planned CLI tool support
    - **Comprehensive Coverage**: Generate both system sounds and custom phrases

Modules:
    audio: Audio data handling and WAV file generation
    providers: TTS provider implementations (Piper, Polly)
    client: Unified client interface for TTS providers
    voicepacks: Voice pack configuration and management

Quick Start:
    Generate a simple sound file using Piper (local TTS):

    >>> from txsoundgen import Client
    >>> # Create a client with the Piper provider
    >>> client = Client(provider='piper')
    >>> # Generate speech from text
    >>> audio = client.process("Battery low")
    >>> # Save to WAV file
    >>> audio.write_wav('battery_low.wav')
    'battery_low.wav'

    Generate sounds using AWS Polly (cloud TTS):

    >>> from txsoundgen import Client
    >>> # Create a client with the Polly provider
    >>> client = Client(provider='polly')
    >>> # Generate speech with SSML support
    >>> audio = client.process('<emphasis>Warning</emphasis> signal lost')
    >>> audio.write_wav('signal_lost.wav')
    'signal_lost.wav'

    Work with voice pack configurations:

    >>> from txsoundgen.voicepacks import VoicePack, VP_DEFAULTS
    >>> # Create a voice pack configuration
    >>> config = {'provider': 'piper', **VP_DEFAULTS['piper']}
    >>> data = {
    ...     'battery_low': 'Battery voltage low',
    ...     'signal_lost': 'Radio signal lost',
    ...     'timer': 'Timer elapsed'
    ... }
    >>> pack = VoicePack('my-sounds', config, data)
    >>> print(f"Created pack '{pack.name}' with {len(pack.data)} sounds")
    Created pack 'my-sounds' with 3 sounds

See Also:
    - EdgeTX Documentation: https://edgetx.org/
    - OpenTX Documentation: https://www.open-tx.org/
    - Piper TTS: https://github.com/rhasspy/piper
    - AWS Polly: https://aws.amazon.com/polly/
"""

import logging
import os

import coloredlogs

from txsoundgen.client import *

# Load settings from environment variables
_environment = os.environ.get("TXSOUNDGEN_ENVIRONMENT", "development")
_loglevel = os.environ.get("TXSOUNDGEN_LOG_LEVEL", "DEBUG").upper()

# Remove any default handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Install coloredlogs on the root logger
_LOGFORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
coloredlogs.install(level=_loglevel, fmt=_LOGFORMAT)
