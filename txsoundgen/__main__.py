"""Main entry point for the txsoundgen module.

This module serves as the entry point when txsoundgen is run as a module using
`python -m txsoundgen`. Currently, this functionality is not fully implemented,
as the module is designed primarily as a library for programmatic use.

Future versions will include a full command-line interface for building voice
packs directly from the command line.

Example:
    Running as a module (currently not functional):

    ```bash
    $ python -m txsoundgen
    # This will display a message indicating the module is not meant to be run this way
    ```

    Planned CLI usage (future implementation):

    ```bash
    # Initialize a voice pack configuration
    $ txsoundgen init --provider piper

    # Build a voice pack from a configuration file
    $ txsoundgen build my-voicepack.yaml
    ```

See Also:
    The tasks.py file contains Invoke tasks that can be used for development
    and building documentation. Use `inv --list` to see available tasks.
"""

import logging

_logger = logging.getLogger(__name__)

_logger.info("Not meant to run like this.")
