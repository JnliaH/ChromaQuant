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
from openpyxl.utils import get_column_letter
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
                 start_cell: str = '',
                 sheet: str = ''):

        # Run DataSet initialization
        super().__init__(data=data,
                         start_cell=start_cell,
                         sheet=sheet)

        # Update the value
        self.update_value()

    """ PROPERTIES """
    # Define the reference property, ONLY DEFINE GETTER
    @property
    def reference(self):
        self.update_value()
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
        if value == '':
            raise ValueError('Table sheet cannot be an empty string.')
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
        try:
            # Get the cell's absolute indices
            self.start_column, self.start_row = self.get_cell_indices(value)
            # Set the starting cell
            self._start_cell = value
        except Exception as e:
            raise ValueError(f'Passed start cell is not valid: {e}')
        self.update_value()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        del self.start_row, self.start_column
        self.update_value()

    """ METHODS """
    # Method to update the value's reference
    def update_reference(self):

        # Get the column letter, adjusting from absolute
        column_letter = get_column_letter(self.start_column + 1)

        # Get the Value name cell
        name_cell = \
            f"'{self._sheet}'!${column_letter}${self.start_row + 1}"
        # Get the Value data cell
        data_cell = \
            f"'{self._sheet}'!${column_letter}${self.start_row + 2}"

        # Get the Value data cell
        # Update the reference object
        self._reference = \
            {'column_letter': column_letter,
             'row': self.start_row + 1,
             'sheet': self._sheet,
             'name_cell': name_cell,
             'data_cell': data_cell}

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
