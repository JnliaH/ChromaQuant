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

import re
from openpyxl.utils import get_column_letter, coordinate_to_tuple
from .. import import_local_packages as ilp
from .. import logging_and_handling as lah
from .formula import Formula

""" LOGGING AND HANDLING """

# Get the logger
logger = lah.setup_logger()

# Get an error logging decorator
error_logging = lah.setup_error_logging(logger)

""" LOCAL PACKAGES """

# Get absolute directories for subpackages
subpack_dir = ilp.get_local_package_directories()

# Import all local packages
hd = ilp.import_from_path("hd", subpack_dir['Handle'])
sg = ilp.import_from_path("sg", subpack_dir['Signal'])

""" CLASS """


# Define the results class
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
    def add_table(self,
                  table_name,
                  data_frame,
                  sheet='Sheet1',
                  start_cell='A1'):

        # If cell is a valid format...
        if self.check_cell_name(start_cell):

            # Get the list of columns
            col_list = data_frame.columns.tolist()
            # Create a new table entry in the tables dictionary
            self.tables[table_name] = {'header':
                                       {'type': 'table',
                                        'sheet': sheet,
                                        'start_cell': start_cell,
                                        'length': len(data_frame),
                                        'columns': col_list
                                       },
                                       'data': data_frame
                                       }
        # Otherwise, raise error
        else:
            raise ValueError(f'Starting cell "{start_cell}" is not valid')
        return None

    # Function for updating a table's column and length headers
    @error_logging
    def update_table(self, table_name):

        # Update the length header
        self.tables[table_name]['header']['length'] = \
            len(self.tables[table_name]['data'])
        
        # Update the column header
        self.tables[table_name]['header']['columns'] = \
            self.tables[table_name]['data'].columns.tolist()

        return None

    # Function to add a new value to the results
    @error_logging
    def add_value(self,
                  value_name,
                  data,
                  sheet='Sheet1',
                  cell='A1'):

        # If cell is a valid format...
        if self.check_cell_name(cell):
            # Create a new value entry in the values dictionary
            self.values[value_name] = {'header':
                                       {'type': 'value',
                                        'sheet': sheet,
                                        'cell': cell
                                       },
                                       'data': data
                                       }
        # Otherwise, raise error
        else:
            raise ValueError(f'Cell "{cell}" is not valid')

        return None

    # Function to add a new column to a table
    @error_logging
    def add_table_column(self,
                         table_name,
                         column_name,
                         column_values=float('nan')):

        # Get a copy of the table DataFrame
        output_dataframe = self.tables[table_name]['data'].copy()

        # Set every entry in the column to column_values
        # If column_values is an iterable, this will iterate
        # through it, otherwise it will set every entry to
        # the same value
        output_dataframe[column_name] = column_values

        # Replace the table DataFrame with the new DataFrame
        self.tables[table_name]['data'] = output_dataframe.copy()

        # Update the column
        self.update_table(table_name)

        return None

    # Function for checking that a passed cell has letters followed by number
    @staticmethod
    def check_cell_name(cell):

        # Initialize tf
        tf = False

        # Define the cell format pattern
        cell_format = '^[A-Za-z]+\\d+$'

        # If the cell matches the expected format, set tf to True
        if re.match(cell_format, cell):
            tf = True

        # Otherwise, pass
        else:
            pass

        return tf

    # Function to add a new Excel formula to a cell or table
    @error_logging
    def add_new_formula(self, formula, value_or_column_name, table=''):

        # TODO: CHANGE SO THERE IS NO NEED TO PASS RESULTS OBJECT TO FORMULA
        # Create a pointers dictionary with the value or column name
        pointers = {'key': value_or_column_name}

        # Get a Formula object instance
        formula_obj = Formula(formula)

        # Create a dictionary containing headers for each value
        value_headers = {value_name:self.values[value_name]['header']
                    for value_name in self.values}

        # Create a dictionary containing headers for each table
        table_headers = {table_name:self.tables[table_name]['header']
                            for table_name in self.tables}

        # If there was no table string...
        if table == '':

            # Process the formula inserts
            formula_obj.process_value_formula_inserts(value_headers, table_headers)

            # Set the corresponding value in the values object to new_formula
            self.values[value_or_column_name] = formula_obj.new_formula

        # Otherwise...
        else:

            # Add a table key-value pair to pointers
            pointers['table'] = table

            # Process the formula inserts
            formula_obj.process_table_formula_inserts(value_headers, table_headers, pointers)

            # Set the corresponding column in the table to new_formula
            self.tables[table]['data'][value_or_column_name] = formula_obj.new_formula

            # Update the table
            self.update_table(table)

        return None
