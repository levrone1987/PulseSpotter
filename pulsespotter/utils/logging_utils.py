import logging


def get_logger(name):
    """
    Sets up a logger for the specified module name.

    Args:
        name (str): The name of the module.

    Returns:
        logging.Logger: Configured logger for the module.
    """
    # Create a logger
    logger = logging.getLogger(name)

    # Set the logging level
    logger.setLevel(logging.DEBUG)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(console_handler)
    return logger
