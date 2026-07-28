# nexus_memory_logger.py

import logging


def get_logger(name):
    """Creates and configures a logger."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
    return logger


if __name__ == "__main__":
    logger = get_logger("NamoNexusLogger")
    logger.info("NamoNexus Memory Logger Initialized.")
