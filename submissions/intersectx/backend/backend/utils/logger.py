import structlog


# --- logging helpers ---
def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    # Creating an object
    logger = structlog.get_logger(name)

    # Setting the threshold of logger to DEBUG
    # logger.setLevel(level)

    return logger
