import logging
import logging.handlers

def create_logger(location_to_log_file,name=__name__):
    
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler = logging.FileHandler(location_to_log_file)
    handler.setFormatter(formatter)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger