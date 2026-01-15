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

from ..logging_and_handling import setup_logger, setup_error_logging
from .formula import Formula
from ..data import Table, Value

""" LOGGING AND HANDLING """

# Get the logger
logger = setup_logger()

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Results class
class Results():

    def __init__(self, output_key, **kwargs):
        """
        __init__ _summary_

        Parameters
        ----------
        output_key : str
            Key assigned to current object in parent dictionary

        """

        # Extract assigned results output key
        self.output_key = output_key

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

    # Function to add a new table to the results
    @error_logging
    def add_table(self, table_name, data_frame, **kwargs):

        # Create a new table entry in the tables dictionary
        self.tables[table_name] = Table(data_frame, **kwargs)

        return None

    # Function to add a new value to the results
    @error_logging
    def add_value(self, value_name, data, **kwargs):

        # Create a new value entry in the values dictionary
        self.values[value_name] = Value(data, **kwargs)

        return None

    # Function to add a new Excel formula to a cell or table
    @error_logging
    def add_new_formula(self, formula, value_or_column_name, table=''):

        # TODO: CHANGE SO THERE IS NO NEED TO PASS RESULTS OBJECT TO FORMULA
        # Create a pointers dictionary with the value or column name
        pointers = {'key': value_or_column_name}

        # Get a Formula object instance
        formula_obj = Formula(formula)

        # Create a dictionary containing headers for each value
        value_headers = {value_name: self.values[value_name]['header']
                         for value_name in self.values}

        # Create a dictionary containing headers for each table
        table_headers = {table_name: self.tables[table_name]['header']
                         for table_name in self.tables}

        # If there was no table string...
        if table == '':

            # Process the formula inserts
            formula_obj.process_value_formula_inserts(value_headers,
                                                      table_headers)

            # Set the corresponding value in the values object to new_formula
            self.values[value_or_column_name] = formula_obj.new_formula

        # Otherwise...
        else:

            # Add a table key-value pair to pointers
            pointers['table'] = table

            # Process the formula inserts
            formula_obj.process_table_formula_inserts(value_headers,
                                                      table_headers,
                                                      pointers)

            # Set the corresponding column in the table to new_formula
            self.tables[table]['data'][value_or_column_name] = \
                formula_obj.new_formula

            # Update the table
            self.update_table(table)

        return None

    # Function for creating a formula by introducing an operator
    # between two references based on those reference's pointers
    def operation_formula(self, ref_1, ref_2, operator):

        # Initialize formula
        formula = f'|{ref_1}|{operator}|{ref_2}|'

        return formula
