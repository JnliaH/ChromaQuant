#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

TOOLS FOR FILE IMPORTING AND EXPORTING

Julia Hancock
Started 1-16-2025

"""

import logging
import os
import pandas as pd
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
def export_to_csv(dataframe, parent, name=''):
    """export_to_csv _summary_

    Parameters
    ----------
    dataframe : dataframe
        Passed Pandas dataframe.
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
def try_open_file(func, path, *args, **kwargs):

    # Predefine the conditional Boolean result
    tf = False

    # Try opening the file, if it works then set tf to True
    try:
        data = func(path, *args, **kwargs)
        tf = True

    # If cannot open file, log and set tf to False
    except Exception as e:
        # logger.info(f'Could not open {path}, got {e}')
        data = []
        tf = False

    return tf, data


# Function to try to open a file with pandas.read_csv
def try_open_csv(path, *args, **kwargs):
    tf, data = try_open_file(pd.read_csv, path, *args, **kwargs)
    return tf, data
