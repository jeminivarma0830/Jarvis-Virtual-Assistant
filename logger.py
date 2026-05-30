"""
core/logger.py  –  Configures logging for the whole app
"""
import logging
import os
from config.settings import LOG_FILE, LOG_LEVEL

def setup_logger():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
