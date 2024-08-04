import logging

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler()  # You can configure other handlers like FileHandler if needed
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
