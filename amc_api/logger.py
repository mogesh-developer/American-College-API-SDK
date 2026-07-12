import logging

logger = logging.getLogger("amc_api")
logger.addHandler(logging.NullHandler())


def setup_logger(level=logging.INFO):
    """Utility function to setup basic logging to console for testing/debugging."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)
