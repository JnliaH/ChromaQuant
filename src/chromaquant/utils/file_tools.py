#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

The File Tools module contains a number of tools used internally to open or
write to data files.

"""

import logging
import os
import pandas as pd
from pandas import DataFrame
from collections.abc import Callable
from typing import Any
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" FUNCTIONS """


# Function to export data to a .csv file
def export_to_csv(dataframe: DataFrame, parent: str, name: str = ''):
    """
    Function that exports data from a pandas DataFrame to a .csv using a
    passed parent directory and name.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        Passed Pandas DataFrame.
    parent : string
        Name of parent directory for exported file.
    name : string
        Name of file to be exported.

    Returns
    -------
    None

    """

    # If the name argument is passed...
    if name:
        # Construct a full path from the passed
        # parent directory and file name
        full_path = os.path.join(parent, name, '.csv')
    # Otherwise...
    else:
        # Set the full path to the parent
        full_path = parent

    # Export the dataframe to the full path
    dataframe.to_csv(full_path, index=False)

    return None


# Function to try to open a file using a passed function
def try_open_file(func: Callable[..., Any], path: str, *args, **kwargs) \
   -> tuple[bool, Any]:
    """
    Function that tries to open a file at path using a function
    passed as func.

    Parameters
    ----------
    func : Callable[..., Any]
        A function that accepts a path (string) and any additional
        positional or keyword arguments and returns some data.
    path : _type_
        A full path to the data file to be opened.

    Returns
    -------
    tf: bool
        A Boolean indicating whether file could be opened (True) or
        not (False).
    data: Any
        The data read from the file at path.

    """

    # Predefine the conditional Boolean result
    tf = False

    # Try opening the file, if it works then set tf to True
    try:
        data = func(path, *args, **kwargs)
        tf = True

    # If cannot open file, log and set tf to False
    except Exception:
        # logger.info(f'Could not open {path}, got {e}')
        data = []
        tf = False

    return tf, data


# Function to try to open a file with pandas.read_csv
def try_open_csv(path: str, *args, **kwargs) -> tuple[bool, Any]:
    """
    Function to try opening a file with pandas.read_csv, passing
    the path and any additional positional or keyword arguments.

    Parameters
    ----------
    path : str
        Path to .csv file.

    Returns
    -------
    tf: bool
        A Boolean indicating whether file could be opened (True) or
        not (False).
    data: Any
        The data read from the file at path.

    """

    tf, data = try_open_file(pd.read_csv, path, *args, **kwargs)

    return tf, data
