"""Voice pack configuration and management.

This module provides data structures and utilities for managing voice pack configurations.
Voice packs are collections of audio files organized by text-to-speech provider settings,
voice selections, and the actual sound data to be generated.

A voice pack represents a complete set of radio sounds (warnings, telemetry announcements,
system messages, etc.) generated with consistent voice and language settings.

Example:
    Creating a voice pack:

    >>> from txsoundgen.voicepacks import VoicePack, VP_DEFAULTS
    >>> config = {
    ...     'provider': 'piper',
    ...     'voice': 'alan',
    ...     'language': 'en_GB'
    ... }
    >>> data = {
    ...     'battery_low': 'Battery low',
    ...     'signal_lost': 'Signal lost',
    ...     'timer_elapsed': 'Timer elapsed'
    ... }
    >>> pack = VoicePack(name='my-sounds', config=config, data=data)
    >>> print(pack)
    VoicePack(name=my-sounds, config={'provider': 'piper', 'voice': 'alan', 'language': 'en_GB'}
"""

VP_DEFAULTS = {
    "piper": {"language": "en-GB", "voice": "alan"},
    "polly": {"language": "en-GB", "voice": "Amy"},
}
"""dict: Default configuration settings for each TTS provider.

This dictionary provides sensible defaults for voice and language settings for each
supported TTS provider. These defaults are used when creating voice packs without
explicit configuration.

Keys:
    - 'piper': Default settings for the Piper TTS provider
    - 'polly': Default settings for the AWS Polly TTS provider

Each provider's defaults include:
    - 'language': The default language code (e.g., 'en-GB')
    - 'voice': The default voice name (e.g., 'alan' for Piper, 'Amy' for Polly)

Example:
    Using defaults to create a configuration:

    >>> from txsoundgen.voicepacks import VP_DEFAULTS
    >>> # Get Piper defaults
    >>> piper_config = VP_DEFAULTS['piper'].copy()
    >>> print(piper_config)
    {'language': 'en-GB', 'voice': 'alan'}
    >>> 
    >>> # Customize the defaults
    >>> piper_config['voice'] = 'jenny'
    >>> print(piper_config)
    {'language': 'en-GB', 'voice': 'jenny'}

    Merge with custom settings:

    >>> custom = {'speed': '0.9'}
    >>> full_config = {**VP_DEFAULTS['polly'], **custom}
    >>> print(full_config)
    {'language': 'en-GB', 'voice': 'Amy', 'speed': '0.9'}
"""


class VoicePack:
    """Class representing a voice pack configuration and data.

    A VoicePack encapsulates all the information needed to generate a complete set of
    radio sounds: the pack name, TTS provider configuration (voice, language, etc.),
    and the actual sound data (text phrases to synthesize).

    This class serves as a data container that can be serialized/deserialized for
    storage or transmission, and provides a clean interface for accessing voice pack
    components.

    Attributes:
        name (str): The unique name/identifier for this voice pack.
        config (dict): Configuration dictionary containing provider settings like
            voice, language, and engine parameters.
        data (dict): Dictionary mapping sound file identifiers to text phrases,
            e.g., {'battery_low': 'Battery low', 'timer': 'Timer elapsed'}.

    Args:
        name (str):
            The name of the voice pack. This typically becomes the filename when
            the pack is exported (e.g., 'my-pack' becomes 'my-pack.zip').
        config (dict):
            Configuration dictionary with TTS provider settings. Should include
            at minimum 'provider' (e.g., 'piper', 'polly') and provider-specific
            settings like 'voice' and 'language'. Additional provider-specific
            options can be included (e.g., 'engine' for Polly).
        data (dict):
            Dictionary mapping sound identifiers to text phrases. Keys should be
            meaningful sound names (e.g., 'battery_low', 'signal_lost') and values
            should be the text to synthesize into speech.

    Example:
        Create a basic voice pack:

        >>> from txsoundgen.voicepacks import VoicePack
        >>> pack = VoicePack(
        ...     name='warning-pack',
        ...     config={'provider': 'piper', 'voice': 'alan', 'language': 'en_GB'},
        ...     data={'warning': 'Warning', 'alert': 'Alert'}
        ... )
        >>> print(pack.name)
        warning-pack
        >>> print(pack.data['warning'])
        Warning

        Create a voice pack with default settings:

        >>> from txsoundgen.voicepacks import VoicePack, VP_DEFAULTS
        >>> config = {'provider': 'piper', **VP_DEFAULTS['piper']}
        >>> pack = VoicePack(
        ...     name='default-pack',
        ...     config=config,
        ...     data={'hello': 'Hello', 'goodbye': 'Goodbye'}
        ... )

        Access voice pack components:

        >>> pack = VoicePack('my-pack', {'provider': 'piper'}, {'msg': 'Hello'})
        >>> print(f"Pack name: {pack.name}")
        Pack name: my-pack
        >>> print(f"Provider: {pack.config['provider']}")
        Provider: piper
        >>> print(f"Message: {pack.data['msg']}")
        Message: Hello

        Create a comprehensive voice pack:

        >>> pack = VoicePack(
        ...     name='radio-warnings',
        ...     config={
        ...         'provider': 'polly',
        ...         'voice': 'Amy',
        ...         'language': 'en-GB',
        ...         'engine': 'neural'
        ...     },
        ...     data={
        ...         'batt_low': 'Battery voltage low',
        ...         'batt_crit': 'Battery critical',
        ...         'signal_lost': 'Radio signal lost',
        ...         'signal_weak': 'Signal strength weak',
        ...         'throttle_high': 'Throttle warning',
        ...         'timer_1': 'Timer one elapsed',
        ...         'timer_2': 'Timer two elapsed',
        ...         'rssi_low': 'RSSI low',
        ...         'rssi_crit': 'RSSI critical'
        ...     }
        ... )
        >>> print(f"Voice pack '{pack.name}' contains {len(pack.data)} sounds")
        Voice pack 'radio-warnings' contains 9 sounds
    """

    def __init__(self, name, config, data) -> None:
        """Initialize a VoicePack instance.

        Args:
            name (str): The voice pack name/identifier.
            config (dict): TTS provider configuration settings.
            data (dict): Sound identifier to text phrase mappings.
        """
        self.name = name
        self.config = config
        self.data = data

    def __repr__(self) -> str:
        """Return a string representation of the VoicePack instance.

        Provides a concise, readable representation of the voice pack showing its
        name and configuration. Useful for debugging and logging.

        Returns:
            str: A string in the format "VoicePack(name=<name>, config=<config>".

        Example:
            >>> pack = VoicePack('test', {'provider': 'piper'}, {'msg': 'Hi'})
            >>> repr(pack)
            "VoicePack(name=test, config={'provider': 'piper'}"
            >>> print(pack)
            VoicePack(name=test, config={'provider': 'piper'}
        """
        return f"VoicePack(name={self.name}, config={self.config}"
