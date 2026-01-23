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

CLASS DEFINITION FOR TABLES

Julia Hancock
Started 01-12-2025

"""

import logging
import pandas as pd
from openpyxl.utils.cell import get_column_letter
from .dataset import DataSet
from ..logging_and_handling import setup_logger, setup_error_logging
from ..utils import match

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Table class
class Table(DataSet):

    def __init__(self, data_frame: pd.DataFrame = None, *args, **kwargs):

        # Create a default DataFrame
        data_frame = data_frame if data_frame is not None else pd.DataFrame()

        # Run DataSet initialization
        super().__init__(data_frame, *args, **kwargs)

        # Update the table
        self.update_table()

    """ PROPERTIES """
    # Define the references property
    # Only give references a getter
    @property
    def references(self):
        self.update_table()
        return self._references

    # Redefining properties to include update_table
    # Data properties
    # Getter
    @property
    def data(self):
        return self._data

    # Setter
    @data.setter
    def data(self, value):
        self._data = value
        self.update_table()

    # Deleter
    @data.deleter
    def data(self):
        del self._data
        self._data = pd.DataFrame()
        self.update_table()

    # Sheet properties
    # Getter
    @property
    def sheet(self):
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value):
        self._sheet = value
        self.update_table()

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet
        self.update_table()

    # Start cell properties
    # Getter
    @property
    def start_cell(self):
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value):
        self._start_cell = value
        self.update_table()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        self.update_table()

    """ METHODS """
    # Method to add a new column to a table
    @error_logging
    def add_table_column(self,
                         column_name,
                         column_values=float('nan')):

        # Set every entry in the column to column_values
        # If column_values is an iterable, this will iterate
        # through it, otherwise it will set every entry to
        # the same value
        self._data[column_name] = column_values

        # Update the table
        self.update_table()

        return None

    # Method to import data
    @error_logging
    def import_csv_data(self, path, **kwargs):
        """Reads .csv at passed path and sets self._data to result.

        Parameters
        ----------
        path : str
            Full path to the data file of interest, including file name.
        data_key : str
            Name to assign imported data when using the "data" object.

        Returns
        -------
        None

        """

        # If the user did not pass an index_col value...
        if 'index_col' not in kwargs:
            # Set index_col to False
            kwargs['index_col'] = False
        # Otherwise, pass
        else:
            pass

        # Read data from the provided directory
        self._data = pd.read_csv(path, **kwargs)

        return None

    # Method to match one dataframe to current data
    def match(self, import_DF, match_config):

        match_data = match(self._data, import_DF, match_config)

        return match_data

    # Method to update column references
    @error_logging
    def update_references(self):

        # Get the indices for the start cell
        start_col_index, start_row_index = \
            self.get_cell_indices(self._start_cell)

        # For every column in columns...
        for column in self.columns:

            # Get the current column's letter
            col_letter = \
                self.get_column_letter_wrt_start_cell(column,
                                                      self._data,
                                                      start_col_index)
            # Update the references object
            self._references[column] = \
                {'column_letter': col_letter,
                 'start_row': start_row_index + 1,
                 'end_row': start_row_index + self.length,
                 'sheet': self._sheet,
                 'length': self.length,
                 'range': (f"'{self._sheet}'!"
                           f"${col_letter}${start_row_index + 1}:"
                           f"${col_letter}${start_row_index + self.length}")}

        return None

    # Method for updating otherwise static Table attributes
    @error_logging
    def update_table(self):

        # Update the length header
        self.length = \
            len(self._data)

        # Update the column header
        self.columns = \
            self._data.columns.tolist()
        # Initialize the references object
        self._references = {}

        # Try to update the references
        # NOTE: will not work if there is no valid sheet or start_cell
        try:
            self.update_references()

        except Exception:
            logger.info('Failed to update references.')
            pass

        return None

    """ STATIC METHODS """
    # Static method to get the letter coordinate of a column in a DataFrame
    # with respect to a starting column index
    @staticmethod
    def get_column_letter_wrt_start_cell(column, df, start_col_index):

        # Get the current column's letter
        col_letter = \
            get_column_letter(start_col_index +
                              df.columns.get_loc(column))

        return col_letter
