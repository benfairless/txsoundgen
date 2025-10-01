"""txsoundgen/client.py."""

from txsoundgen.providers import Piper, Polly


class Client:
    """Client class for processing sounds using various providers."""

    def __init__(self, provider="piper") -> None:
        """Initialize the Client with the specified provider."""
        match provider:
            case "piper":
                self.instance = Piper()
            case "polly":
                self.instance = Polly()
            case _:
                raise ValueError("provider")

    # called when an attribute is not found:
    def __getattr__(self, name):
        """Delegate attribute access to the provider instance."""
        return self.instance.__getattribute__(name)
