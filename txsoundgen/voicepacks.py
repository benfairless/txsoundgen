"""Module for managing voice pack configurations."""

VP_DEFAULTS = {
    "piper": {"language": "en-GB", "voice": "alan"},
    "polly": {"language": "en-GB", "voice": "Amy"},
}


class VoicePack:
    """Class representing a voice pack configuration."""

    def __init__(self, name, config, data) -> None:
        """Initialize a VoicePack instance."""
        self.name = name
        self.config = config
        self.data = data

    def __repr__(self) -> str:
        """Return a string representation of the VoicePack instance."""
        return f"VoicePack(name={self.name}, config={self.config}"
