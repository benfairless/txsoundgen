""".. include:: ../README.md"""

import os
import logging
import coloredlogs


loglevel = os.environ.get("TXSOUNDGEN_LOG_LEVEL", "DEBUG").upper()
logger = logging.getLogger(__name__)
# logger = logging.getLogger()
logger.setLevel(loglevel)

# fmt = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] %(message)s','%Y-%m-%d %H:%M:%S')
LOGFORMAT = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
coloredlogs.install(level="DEBUG", logger=logger, fmt=LOGFORMAT)
# stdout_handler = logging.StreamHandler()
# stdout_handler.setLevel(loglevel)
# stdout_handler.setFormatter(fmt)
# logger.addHandler(stdout_handler)

# https://alexandra-zaharia.github.io/posts/make-your-own-custom-color-formatter-with-python-logging/
# https://pypi.org/project/coloredlogs/

environment = os.environ.get("TXSOUNDGEN_ENVIRONMENT", "development")
