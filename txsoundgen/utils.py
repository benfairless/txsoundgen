"""This sub-module contains low-level utilities used to make things simple.

Contents:
    - `merge_config()` - Merges provided configuration dictionary with default configuration.
"""

default_config = {
    "language": "en-GB",
    "voice": "Amy",
    "engine": "standard",
    "extension": "wav",
    "name": "default",
}
"""Default configuration used for numerous objects, mainly used to provide configuration
to Amazon Polly.
"""


def merge_config(config: dict = None):
    """Merges provided configuration dictionary with default configuration.

    This is used to allow users to override any values from the default configuration,
    even in a reasonably complex structure.

    Args:
        config (dict): Dictionary containing configuration for txsoundgen.

    Returns:
        (dict): A dictionary containing the configuration, merged with the default values.

    Later down the line, this may provide validation of configuration parameters.

    Example:
        ```python
        >>> import txsoundgen.utils
        >>> my_dict = {"language": "en-US"}
        >>> txsoundgen.utils.merge_config(my_dict)
        {
            'language': 'en-US',
            'voice': 'Amy',
            'engine': 'standard',
            'extension': 'wav',
            'name': 'default'
        }

        ```
    """
    if not config:
        config = {}
    return {**default_config, **config}  # Combine default config with provided conf
