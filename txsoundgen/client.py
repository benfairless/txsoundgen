"""TTS client interface for simplified provider access.

This module provides a unified client interface for working with different TTS providers.
The Client class acts as a factory and proxy, allowing you to instantiate and use any
supported TTS provider through a single, consistent API.

Example:
    Using the client with Piper:

    >>> from txsoundgen.client import Client
    >>> client = Client(provider='piper')
    >>> audio = client.process("Battery voltage low")
    >>> audio.write_wav('battery_warning.wav')
    'battery_warning.wav'

    Switching providers is simple:

    >>> # Use Polly instead
    >>> client = Client(provider='polly')
    >>> audio = client.process("Signal strength excellent")
    >>> audio.write_wav('signal.wav')
    'signal.wav'
"""

from txsoundgen.providers import Piper, Polly


class Client:
    """Client class for processing sounds using various TTS providers.

    The Client class provides a convenient way to work with different TTS providers
    without needing to import and instantiate provider classes directly. It acts as
    both a factory (creating the appropriate provider instance) and a proxy (forwarding
    method calls to the underlying provider).

    This design allows for easy provider switching and cleaner application code. All
    methods and attributes of the underlying provider are accessible through the client
    via Python's attribute delegation mechanism.

    Attributes:
        instance: The underlying provider instance (Piper or Polly).

    Args:
        provider (str, optional):
            The name of the TTS provider to use. Supported values are:
            - 'piper': Use the local Piper TTS engine (default)
            - 'polly': Use AWS Polly cloud TTS service

    Raises:
        ValueError: If an unsupported provider name is specified.

    Example:
        Basic usage with default provider:

        >>> from txsoundgen.client import Client
        >>> # Uses Piper by default
        >>> client = Client()
        >>> audio = client.process("Throttle warning")
        >>> audio.write_wav('throttle.wav')
        'throttle.wav'

        Specify provider explicitly:

        >>> # Use Piper
        >>> piper_client = Client(provider='piper')
        >>> audio1 = piper_client.process("Hello from Piper")
        >>> 
        >>> # Use Polly
        >>> polly_client = Client(provider='polly')
        >>> audio2 = polly_client.process("Hello from Polly")

        Access provider-specific methods:

        >>> client = Client(provider='piper')
        >>> # Download a voice model (Piper-specific method)
        >>> client.download_voice('en_GB-alan-medium')
        >>> # Generate speech
        >>> audio = client.process("Voice model ready")

        Use in a function to abstract provider choice:

        >>> def generate_alert(message, provider='piper'):
        ...     client = Client(provider=provider)
        ...     audio = client.process(message)
        ...     audio.write_wav(f'alert_{provider}.wav')
        ...     return audio
        >>> 
        >>> # Generate with Piper
        >>> generate_alert("Low fuel", provider='piper')
        >>> # Generate with Polly
        >>> generate_alert("Low fuel", provider='polly')

        Generate multiple sounds with the same client:

        >>> client = Client(provider='piper')
        >>> warnings = ["Battery low", "Signal lost", "Timer elapsed"]
        >>> for i, warning in enumerate(warnings):
        ...     audio = client.process(warning)
        ...     audio.write_wav(f'warning_{i}.wav')

    Note:
        The client delegates all attribute access to the underlying provider instance,
        so you can use any provider-specific methods or attributes directly through
        the client object.
    """

    def __init__(self, provider="piper") -> None:
        """Initialize the Client with the specified TTS provider.

        Args:
            provider (str, optional): The TTS provider to use ('piper' or 'polly').
                Defaults to 'piper'.

        Raises:
            ValueError: If the provider name is not 'piper' or 'polly'.
        """
        match provider:
            case "piper":
                self.instance = Piper()
            case "polly":
                self.instance = Polly()
            case _:
                raise ValueError("provider")

    # called when an attribute is not found:
    def __getattr__(self, name):
        """Delegate attribute access to the provider instance.

        This method enables the client to act as a transparent proxy for the underlying
        provider instance. Any attribute or method that doesn't exist on the Client
        itself is automatically forwarded to the provider instance.

        Args:
            name (str): The name of the attribute or method being accessed.

        Returns:
            The attribute or method from the underlying provider instance.

        Raises:
            AttributeError: If the attribute doesn't exist on the provider instance either.

        Example:
            >>> client = Client(provider='piper')
            >>> # The 'process' method doesn't exist on Client,
            >>> # so it's delegated to the Piper instance
            >>> audio = client.process("Test")
            >>> # Provider-specific attributes are also accessible
            >>> print(client.install_dir)  # Accesses Piper's install_dir
            'resources/piper'
        """
        return self.instance.__getattribute__(name)
