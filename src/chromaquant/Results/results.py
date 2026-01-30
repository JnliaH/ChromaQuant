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
import openpyxl
import pandas as pd
from ..data import Table, Value
from .reporting_tools import report_table, report_value
from ..logging_and_handling import setup_logger, setup_error_logging
from ..formula import Formula
from typing import Any

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

    def __init__(self):
        """

        """

        # Initialize the tables dictionary
        self.tables: dict[str, Table] = {}

        # Initialize the values dictionary
        self.values: dict[str, Value] = {}

    # TODO: add functions to iterate on existing table/value nicknames
    # to create new default names if none are provided. Currently,
    # tables and values will be overwritten if no nickname provided

    """ METHODS """
    # Method to add a new Excel formula to a cell or table based
    # on a passed formula string
    @error_logging
    def add_formula(self, formula: Formula):

        # Create a dictionary containing references for each value
        value_references: dict[str, dict[str, Any]] = \
            {value_name: self.values[value_name].reference for value_name in self.values}

        # Create a dictionary containing references for each table
        table_references = {table_name: self.tables[table_name].reference
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

    # Method to add a new table to the results
    @error_logging
    def add_table(self,
                  table_instance: Table,
                  table_nickname: str = 'table1'):

        # Create a new table entry in the tables dictionary
        self.tables[table_nickname] = table_instance

        # Create a pointer for the table

        return None

    # Method to add a new value to the results
    @error_logging
    def add_value(self,
                  value_instance: Value,
                  value_nickname: str = 'value1'):

        # Create a new value entry in the values dictionary
        self.values[value_nickname] = value_instance

        return None

    # Method to write passed Results to Excel
    @error_logging
    def report_results(self,
                       path: str = 'report.xlsx'):

        # Write Tables
        # NOTE: Uses pandas ExcelWriter with xlsxwriter
        # With the writer open...
        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:

            # For every Table in Results...
            for table_nickname, table in self.tables.items():
                # Write the Table to Excel
                report_table(table, writer)

        # Write Values
        # NOTE: Uses custom openpyxl writer
        # Reopen the Excel workbook
        workbook = openpyxl.load_workbook(filename=path)

        # For every Value in Results...
        for value_nickname, value in self.values.items():
            # Write the Value to Excel
            report_value(value, workbook, value_nickname)

        # Save and close the Excel workbook
        workbook.save(path)

        return None

    """ STATIC METHODS """
    # Method to get a formula insert for a DataSet's pointer
    @staticmethod
    def get_insert(key: str,
                   table: str = '',
                   range: bool = False) -> str:

        # If table is not provided...
        if table == '':
            # Set insert to a Value's insert
            dataset_insert = f'|key: {key}|'

        # Otherwise...
        else:

            # If range is True...
            if range is True:
                # Set insert to a Table's column range insert
                dataset_insert = f'|table: {table}, key: {key}, range: True|'

            # Otherwise...
            else:
                # Set insert to Table's column insert
                dataset_insert = f'|table: {table}, key: {key}|'

        return dataset_insert

    # Method to get a DataSet's pointer
    @staticmethod
    def get_pointer(key: str,
                    table: str = '',
                    range: bool = False) -> dict[str, str]:

        # If table is not provided...
        if table == '':
            # Get value pointer
            dataset_pointer = {'key': key}

        # Otherwise...
        else:

            # If range is True...
            if range is True:
                # Set pointer to a Table's column range pointer
                dataset_pointer = {'key': key, 'table': table, 'range': 'True'}

            # Otherwise...
            else:
                # Set pointer to Table's column pointer
                dataset_pointer = {'key': key, 'table': table}

        return dataset_pointer
