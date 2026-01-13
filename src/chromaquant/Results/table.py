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

import pandas as pd
from openpyxl.utils.cell import coordinate_from_string, \
                                column_index_from_string, \
                                get_column_letter
from .dataset import DataSet
from .. import logging_and_handling as lah


""" LOGGING AND HANDLING """

# Get the logger
logger = lah.setup_logger()

# Get an error logging decorator
error_logging = lah.setup_error_logging(logger)

""" CLASS """


class Table(DataSet):

    def __init__(self,
                 data_frame=pd.DataFrame(),
                 *args,
                 **kwargs):

        # Run DataSet initialization
        super().__init__(*args, **kwargs)

        # Initialize data variable
        self.data = data_frame

        # Update the table
        self.update_table()

    # Method to update column references
    @error_logging
    def update_references(self):

        # Initialize the references object
        self.references = {}

        # Split the start cell string into individual coordinates
        start_col_letter, start_row = \
            coordinate_from_string(self._start_cell)

        # Get the starting column's index from its letter
        start_col_index = column_index_from_string(start_col_letter)

        # For every column in columns...
        for column in self.columns:

            # Get the current column's letter
            col_letter = \
                get_column_letter(start_col_index +
                                  self.data.columns.get_loc(column))

            # Update the references object
            self.references[column] = \
                {'column_letter': col_letter,
                 'start_row': start_row + 1,
                 'end_row': start_row + self.length,
                 'sheet': self._sheet,
                 'range': (f"'{self._sheet}'!"
                           f"${col_letter}${start_row + 1}:"
                           f"${col_letter}${start_row + self.length}")}

        return None

    # Method for updating otherwise static Table attributes
    @error_logging
    def update_table(self):

        # Update the length header
        self.length = \
            len(self.data)

        # Update the column header
        self.columns = \
            self.data.columns.tolist()

        # Try to update the references
        # NOTE: will not work if there is no sheet or start_cell
        try:
            self.update_references()
        except AttributeError as e:
            logger.info(e)
            pass

        return None

    # Method to add a new column to a table
    @error_logging
    def add_table_column(self,
                         column_name,
                         column_values=float('nan')):

        # Set every entry in the column to column_values
        # If column_values is an iterable, this will iterate
        # through it, otherwise it will set every entry to
        # the same value
        self.data[column_name] = column_values

        # Update the table
        self.update_table()

        return None
