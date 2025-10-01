""".. include:: ../README.md"""

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
