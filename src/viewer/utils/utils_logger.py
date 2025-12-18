import logging
from Typing import Any

def setup_logger(name: str="streamlit_app") -> Any:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Prevent duplicate handlers
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
