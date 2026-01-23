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

CLASS DEFINITION FOR PROCESSING AND EXPORTING RESULTS

Julia Hancock
Started 12-10-2025

"""

import logging
from ..logging_and_handling import setup_logger, setup_error_logging
from ..formula import Formula

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Results class
class Results():

    def __init__(self, **kwargs):
        """

        Parameters
        ----------

        """

        # Extract passed keywork arguments
        for key, value in kwargs.items():
            # Define a prefix
            prefix = 'results_kwarg'
            # Create an attribute name using the defined prefix
            attribute_name = prefix + '_' + key
            # Set attribute using name and key-value pair
            setattr(self, attribute_name, value)

        # Initialize the tables dictionary
        self.tables = {}

        # Initialize the values dictionary
        self.values = {}

    # TODO: add functions to iterate on existing table/value nicknames
    # to create new default names if none are provided. Currently,
    # tables and values will be overwritten if no nickname provided

    # Function to add a new table to the results
    @error_logging
    def add_table(self, table_instance, table_nickname='table1'):

        # Create a new table entry in the tables dictionary
        self.tables[table_nickname] = table_instance

        return None

    # Function to add a new value to the results
    @error_logging
    def add_value(self, value_instance, value_nickname='value1'):

        # Create a new value entry in the values dictionary
        self.values[value_nickname] = value_instance

        return None

    # Function to add a new Excel formula to a cell or table based
    # on a passed formula string
    @error_logging
    def add_formula(self, formula: Formula):

        # Create a dictionary containing references for each value
        value_references = {value_name: self.values[value_name].reference
                            for value_name in self.values}

        # Create a dictionary containing references for each table
        table_references = {table_name: self.tables[table_name].references
                            for table_name in self.tables}

        # Get the new formulas
        formula.insert_references(value_references, table_references)

        # If there is a 'table' and 'key' in the formula's pointer...
        if 'table' in formula.pointer and 'key' in formula.pointer:

            # Set the corresponding column in the table to new_formula
            self.tables[formula.pointer['table']].data[
                formula.pointer['key']] = \
                formula.referenced_formulas

        # Otherwise, if there is a 'key' in the formula's pointer...
        elif 'key' in formula.pointer:

            # Set the corresponding value to new_formula
            self.values[formula.pointer['key']].data = \
                formula.referenced_formulas

        # Otherwise, raise an error
        else:
            error_var = "Formula object has no 'key' or 'table' in its pointer"
            raise KeyError(error_var)

        return None
