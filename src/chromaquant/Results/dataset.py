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

CLASS DEFINITION FOR DATASETS

Julia Hancock
Started 01-12-2025

"""

from .. import logging_and_handling as lah

""" LOGGING AND HANDLING """

# Get the logger
logger = lah.setup_logger()

# Get an error logging decorator
error_logging = lah.setup_error_logging(logger)

""" CLASS """


# Define the DataSet class
class DataSet():

    def __init__(self, *args, **kwargs):

        # Check if passed any positional arguments, raise error if so
        if args:
            raise TypeError('Variable positional arguments are not'
                            'permitted when creating an instance of Table ')

        # Initialize class attributes
        self.type = 'table'
        self._start_cell = '$A$1'
        self._sheet = 'Sheet1'

        # Define the permitted keyword arguments
        self.permitted_kwargs = ['sheet', 'start_cell']

        # Get class attributes from passed variable keyword arguments
        self.create_attributes_kwargs(kwargs)

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

    # Function to create instance attributes for each passed keyword argument
    def create_attributes_kwargs(self, kwargs):

        # For every key-value pair in kwargs...
        for key, value in kwargs.items():

            # If the current key is not permitted, raise an error
            if key not in self.permitted_kwargs:
                raise ValueError(f'{key} is not a valid argument')

            # Otherwise...
            else:
                # If the key is 'sheet' or 'start_cell', add leading underscore
                if key == 'sheet' or key == 'start_cell':
                    setattr(self, f'_{key}', value)
                # Otherwise, set attribute using key-value pair normally
                else:
                    setattr(self, key, value)

        return None
