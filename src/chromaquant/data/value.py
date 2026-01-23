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

import logging
from openpyxl.utils.cell import coordinate_from_string
from .dataset import DataSet
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Value class
class Value(DataSet):

    def __init__(self,
                 data=float('nan'),
                 *args,
                 **kwargs):

        # Run DataSet initialization
        super().__init__(data, *args, **kwargs)

        # Update the value
        self.update_value()

    """ PROPERTIES """
    # Define the reference property, ONLY DEFINE GETTER
    @property
    def reference(self):
        return self._reference

    # Redefining properties to include update_value
    # Data properties
    # Getter
    @property
    def data(self):
        return self._data

    # Setter
    @data.setter
    def data(self, value):
        self._data = value
        self.update_value()

    # Deleter
    @data.deleter
    def data(self):
        del self._data
        self.update_value()

    # Sheet properties
    # Getter
    @property
    def sheet(self):
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value):
        self._sheet = value
        self.update_value()

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet
        self.update_value()

    # Start cell properties
    # Getter
    @property
    def start_cell(self):
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value):
        self._start_cell = value
        self.update_value()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        self.update_value()

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
             'sheet': self._sheet,
             'cell': f"'{self._sheet}'!${col_letter}${row_index}"}

        return None

    # Method to update the value
    def update_value(self):

        # Initialize the reference object
        self._reference = {}

        # Try to update the reference
        # NOTE: will not work if there is no valid sheet or start_cell
        try:
            self.update_reference()
        except Exception as e:
            logger.info(e)
            pass

        return None
