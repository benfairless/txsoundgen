import logging
from txsoundgen.providers import Polly, Piper

logger = logging.getLogger(__name__)

logger.info("Not meant to run like this.")

SAY = "Welcome to the world of speech synthesis!"
piper = Piper().process(SAY)
# polly = Polly().process(SAY)
# piper.write_wav("test_piper.wav")
# polly.write_wav("test_polly.wav")
