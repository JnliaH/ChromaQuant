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

from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Get the logger
logger = setup_logger()

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the DataSet class
class DataSet():

    def __init__(self, data=float('nan'), *args, **kwargs):

        # Check if passed any positional arguments, raise error if so
        if args:
            raise TypeError('Variable positional arguments are not'
                            'permitted when creating an instance of Table ')

        # Initialize class attributes
        self.type = 'table'
        self._start_cell = '$A$1'
        self._sheet = 'Sheet1'

        # Initialize data attribute
        self._data = data

        # Define the permitted keyword arguments
        self.permitted_kwargs = ['sheet', 'start_cell']

        # Get class attributes from passed variable keyword arguments
        self.create_attributes_kwargs(kwargs)

    """ PROPERTIES """
    # Data property
    # Getter
    @property
    def data(self):
        return self._data

    # Setter
    @data.setter
    def data(self, value):
        self._data = value

    # Deleter
    @data.deleter
    def data(self):
        del self._data

    # Sheet properties
    # Getter
    @property
    def sheet(self):
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value):
        self._sheet = value

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet

    # Start cell properties
    # Getter
    @property
    def start_cell(self):
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value):
        self._start_cell = value

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell

    """ METHODS """
    # Method to create instance attributes for each passed keyword argument
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

    """ STATIC METHODS """
    # Method to loop through keys in a passed dictionary and
    # check them against a list of permitted keys or dictionary
    # with permitted keys
    @staticmethod
    def check_dict_keys(dictionary, permitted):

        # For every key-value pair in the dictionary...
        for key, value in dictionary.items():

            # If the current key is not permitted, raise an error
            if key not in permitted:
                raise ValueError(f'{key} is not a valid argument')

            # Otherwise, pass
            else:
                pass

        return None
