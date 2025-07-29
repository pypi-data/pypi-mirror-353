import logging

from chaitin_rpa.config import config

logger = logging.getLogger(__name__)
logging.basicConfig(filename="chaitin_rpa.log", level=config.LOG_LEVEL)
