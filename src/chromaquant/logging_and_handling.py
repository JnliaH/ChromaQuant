#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The Logging and Handling module contains functions used internally by most
modules for logging and handling errors.

"""

import logging
from functools import wraps
from collections.abc import Callable
from typing import Any


# Function to format logger
def setup_logger(logger: logging.Logger) -> logging.Logger:
    """
    Function that formats a logger.

    Parameters
    ----------
    logger : logging.Logger
        Logger to format.

    Returns
    -------
    new_logger: logging.Logger
        Logger post-formatting.

    """

    # Check if logger has handlers, clear if so
    if (logger.hasHandlers()):
        logger.handlers.clear

    # Add a handler for the console
    console_handler = logging.StreamHandler()
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
def setup_error_logging(logger: logging.Logger) -> \
   Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Function that creates a decorator to log errors while handling them.

    Returns
    -------
    decorator: Callable[[Callable[..., Any]], Callable[..., Any]]
        Decorator used to wrap functions.

    """

    # Decorator to log and handle errors
    def error_logging(f: Callable[..., Any]) -> Callable[..., Any]:
        """
        Decorator for logging and handling.

        Parameters
        ----------
        f : Callable[..., Any]
            Function to decorate.

        Returns
        -------
        decorated_func : Callable[..., Any]
            Decorated function.

        """

        # Define decorated function (wrapper)
        @wraps(f)
        def decorated_func(*args: Any, **kwargs: Any) -> Any:
            """
            Decorated function.

            Returns
            -------
            result : Any
                Result from function.

            """

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
