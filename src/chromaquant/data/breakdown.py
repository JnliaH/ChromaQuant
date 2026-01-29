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

CLASS DEFINITION FOR BREAKDOWN

Julia Hancock
Started 01-28-2026

"""

import logging
from openpyxl.utils import get_column_letter
from pandas import DataFrame
from .dataset import DataSet
from .table import Table
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS"""


# Class definition for Breakdown
class Breakdown(DataSet):

    # Initialize
    def __init__(self,
                 start_cell: str = '',
                 sheet: str = '',
                 conditional_aggregate: str = 'SUMIFS'):

        # Run DataSet initialization
        super().__init__(data=DataFrame(),
                         start_cell=start_cell,
                         sheet=sheet)

        # Create attributes
        self.data = DataFrame()
        self.allowed_conditional_aggregates = ['SUMIFS',
                                               'COUNTIFS',
                                               'AVERAGEIFS',
                                               'MINIFS',
                                               'MAXIFS']

        # If the conditional aggregate is not equal to an expected value...
        if conditional_aggregate not in self.allowed_conditional_aggregates:
            # Raise an error
            raise ValueError(('Conditional aggregate not recognized: '
                              f'{conditional_aggregate}'))
        # Otherwise, assign to an attribute
        else:
            self.conditional_aggregate = conditional_aggregate

    """ METHODS """
    # Method to create a conditional aggregate formula based on criteria
    def create_conditional_aggregate_formula(self,
                                             table: Table,
                                             criteria: dict[str, str],
                                             summarize_column: str = ''
                                             ):

        # Create a blank formula template
        formula_template = ''

        # If the conditional aggregate is COUNTIFS...
        if self.conditional_aggregate == 'COUNTIFS':

            # Create a COUNTIFS-specific inner formula template
            formula_template = ''

        # Otherwise, if summarize column is not empty...
        elif summarize_column != '':
            # Create an inner formula template
            formula_template = f'{table.reference[summarize_column]['range']}'

        # Otherwise, raise an error
        else:
            raise ValueError(('Argument summarize_column cannot be blank for'
                              'conditional aggregates besides COUNTIFS'))

        # For every key-value pair in criteria...
        for cell_or_range in criteria:

            # Add criteria range to formula_template
            formula_template += f', {cell_or_range}'
            # Add criteria to formula_template
            formula_template += f', "{criteria[cell_or_range]}"'

        # Get the final formula by wrapping in the passed conditional aggregate
        formula = f'={self.conditional_aggregate}({formula_template})'

        return formula

    # Method to create a one-dimensional breakdown
    def create_1D(self,
                  table: Table,
                  group_by_column: str,
                  summarize_column: str,
                  groups_to_summarize: list[str] = None):

        # If groups_to_summarize is not none...
        if groups_to_summarize is not None:
            # Set unique_groups to a shallow copy of groups_to_summarize
            unique_groups = groups_to_summarize[:]

        # Otherwise...
        else:
            # Get a list of unique values in Table in the group by column
            unique_groups = table.data[group_by_column].unique()

            # Sort the list of unique groups
            unique_groups.sort()

        # Create an empty 1D DataFrame using the unique groups
        self.data = DataFrame({group: [None] for group in unique_groups})

        # Create an index for the current header cell
        header_cell_index = 0

        # For every group...
        for group in unique_groups:

            # Get the start cell's absolute indices
            absolute_start_col, absolute_start_row = \
                self.get_cell_indices(self.start_cell)

            # Get the current header's column and row
            start_col = \
                get_column_letter(absolute_start_col + 1 + header_cell_index)
            start_row = \
                absolute_start_row + 1

            # Get the current header cell
            header_cell = f'{start_col}${start_row}'

            # Define the criteria dictionary
            criteria = {header_cell: group}

            print(criteria)
            # Get a formula string
            formula_string = \
                self.create_conditional_aggregate_formula(table,
                                                          criteria,
                                                          summarize_column
                                                          )

            # Add the formula string to the current group entry
            self.data[group] = [formula_string]

        return None

    # Method to create a two-dimensional breakdown
    def create_2D(self,
                  group_by_1,
                  group_by_2,
                  data_column):

        return None

    def merge_1D(self,
                 breakdown_list):

        return None

    def merge_2D(self,
                 breakdown_list):

        return None

    """ STATIC METHODS """

    # Base conditional aggregate method
    @staticmethod
    def _wrap_conditional_aggregate(inner, outer):

        # If the inner starts with an equals sign...
        if inner[0] == '=':
            # Remove the equals sign
            inner = inner[1:]

        # Otherwise, pass
        else:
            pass

        # Get the formula string
        formula_string = f"={outer}({inner})"

        return formula_string
