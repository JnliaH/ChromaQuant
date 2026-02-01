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
from ..data import Table, Value, Breakdown
from .reporting_tools import report_table, report_value
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

    def __init__(self):
        """

        """

        # Initialize the tables list
        self.tables: list[Table] = []

        # Initialize the values list
        self.values: list[Value] = []

        # Initialize the breakdowns list
        self.breakdowns: list[Breakdown] = []

        # Initialize the DataSet references dictionary
        self.dataset_references = {}

        # Create an empty cache for added formulas
        self._formula_cache = []

    """ METHODS """
    # Method to add a new Breakdown to the results
    @error_logging
    def add_breakdown(self, breakdown: Breakdown):

        # Set the breakdown's mediator to the current object
        breakdown.mediator = self
        # Add the breakdown to the breakdowns list
        self.breakdowns.append(breakdown)

        return None

    # Method to add a new Excel formula to a cell or table based
    # on a passed formula string
    @error_logging
    def add_formula(self, formula: Formula):

        # Update dataset references
        self.update_references()

        # Add a formula to the cache
        self._formula_cache.append(formula)

        # Get the new formulas
        formula.insert_references(self.dataset_references)

        # If there is a 'table' and 'key' in the formula's attributes...
        if formula.table_pointer != '' and formula.key_pointer != '':

            # For every table...
            for i in range(len(self.tables)):

                # If the table id is equal to the formula's...
                if self.tables[i].id == formula.table_pointer:

                    # Add the new formulas to the pointed column
                    self.tables[i].data[formula.key_pointer] = \
                        formula.referenced_formulas

                # Otherwise, pass
                else:
                    pass

        # Otherwise, if there is a 'key' in the formula's pointer...
        elif formula.key_pointer != '':

            # For every key...
            for i in range(len(self.values)):

                # If the table id is equal to the formula's...
                if self.values[i].id == formula.key_pointer:

                    # Add the new formulas to the pointed column
                    self.values[i].data = \
                        formula.referenced_formulas

                # Otherwise, pass
                else:
                    pass

        # Otherwise, raise an error
        else:
            raise KeyError("Formula has no defined output location.")

        return None

    # Method to add a new table to the results
    @error_logging
    def add_table(self, table: Table):

        # Add the table to the tables list
        self.tables.append(table)

        return None

    # Method to add a new value to the results
    @error_logging
    def add_value(self, value: Value):

        # Add the value to the values list
        self.values.append(value)

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
            for table in self.tables:
                # Write the Table to Excel
                report_table(table, writer)

        # Write Values
        # NOTE: Uses custom openpyxl writer
        # Reopen the Excel workbook
        workbook = openpyxl.load_workbook(filename=path)

        # For every Value in Results...
        for value in self.values:
            # Write the Value to Excel
            report_value(value, workbook)

        # Save and close the Excel workbook
        workbook.save(path)

        return None

    # Method to update all datasets
    @error_logging
    def update_datasets(self):

        # For every formula in the formula cache...
        for formula in self._formula_cache:
            # Add a formula to results
            self.add_formula(formula)

        # For every breakdown...
        for breakdown in self.breakdowns:
            # Get the method used to construct the breakdown
            breakdown_constructor = breakdown._breakdown_cache['function']
            # Reformulate the breakdown based on its cache
            breakdown_constructor(**breakdown._breakdown_cache['arguments'])

        return None

    # Method to update all dataset references
    @error_logging
    def update_references(self):

        # Add table references for each table
        for table in self.tables:
            self.dataset_references[table.id] = table.reference

        # Add value references for each value
        for value in self.values:
            self.dataset_references[value.id] = value.reference

        return None
