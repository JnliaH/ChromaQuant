"""
COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

FUNCTIONS FOR HANDLING LOGGING AND ERRORS

Julia Hancock
Started 1-7-2026

"""

import logging
from functools import wraps


# Function to initialize and format logger
def setup_logger():

    # Initialize logger
    logger = logging.getLogger(__name__)
    console_handler = logging.StreamHandler()

    # Add a handler for the console
    logger.addHandler(console_handler)

    # Create a formatter object
    formatter = logging.Formatter(
                "{asctime} - [{name:^8s}][{levelname:^8s}] {message}",
                style='{',
                datefmt='%Y-%m-%d %H:%M')

    # Set the console handler's format using the new formatter
    console_handler.setFormatter(formatter)

    # Set logger level - NOTE: Change before commit if debugging
    logger.setLevel(logging.INFO)

    return logger


# Function that sets up a decorator to log errors while handling them
def setup_error_logging(logger):

    # Decorator to log and handle errors
    def error_logging(f):

        # Define decorated function (wrapper)
        @wraps(f)
        def decorated_func(*args, **kwargs):

            # Try to get the function's result
            try:
                result = f(*args, **kwargs)
                return result

            # Log errors if they occur
            except Exception as e:
                logger.error(e)
                raise

        return decorated_func

    return error_logging
