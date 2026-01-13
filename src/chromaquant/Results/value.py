#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

CLASS DEFINITION FOR VALUES

Julia Hancock
Started 01-12-2025

"""

from openpyxl.utils.cell import coordinate_from_string
from .dataset import DataSet
from .. import logging_and_handling as lah

""" LOGGING AND HANDLING """

# Get the logger
logger = lah.setup_logger()

# Get an error logging decorator
error_logging = lah.setup_error_logging(logger)

""" CLASS """


# Define the Value class
class Value(DataSet):

    def __init__(self, data, *args, **kwargs):

        # Run DataSet initialization
        super().__init__(*args, **kwargs)

        # Initialize data attribute
        self.data = data

        # Update the value
        self.update_value()

    """ PROPERTIES """
    # Define the reference property
    @property
    def reference(self):
        return self._reference

    """ METHODS """
    # Method to update the value's reference
    def update_reference(self):

        # Get the column and row for the start cell
        col_letter, row_index = \
            coordinate_from_string(self._start_cell)

        # Update the reference object
        self._reference = \
            {'column_letter': col_letter,
             'row': row_index,
             'sheet': self._sheet}

        return None

    # Method to update the value
    def update_value(self):

        # Initialize the reference object
        self._reference = {}

        # Try to update the reference
        # NOTE: will not work if there is no valid sheet or start_cell
        try:
            self.update_reference()
        except AttributeError as e:
            logger.info(e)
            pass

        return None
