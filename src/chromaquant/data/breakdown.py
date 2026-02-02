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
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from ..results import Results
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
                 conditional_aggregate: str = 'SUMIFS',
                 header: str = '',
                 results: Results = None):

        # Run DataSet initialization
        super().__init__(data=DataFrame(),
                         start_cell=start_cell,
                         sheet=sheet,
                         header=header,
                         results=results)

        # Create attributes
        self.data = DataFrame()
        self.allowed_conditional_aggregates = ['SUMIFS',
                                               'COUNTIFS',
                                               'AVERAGEIFS',
                                               'MINIFS',
                                               'MAXIFS']
        self._breakdown_cache = {}

        # If the conditional aggregate is not equal to an expected value...
        if conditional_aggregate not in self.allowed_conditional_aggregates:
            # Raise an error
            raise ValueError(('Conditional aggregate not recognized: '
                              f'{conditional_aggregate}'))
        # Otherwise, assign to an attribute
        else:
            self.conditional_aggregate = conditional_aggregate

    """ PROPERTIES """
    # Data properties - GETTER ONLY
    # Getter
    @property
    def data(self) -> Any:
        return self._data

    # Setter
    @data.setter
    def data(self, value: DataFrame | None):
        self._data = value

    # Deleter
    @data.deleter
    def data(self):
        del self._data
        self._data = DataFrame()

    # Sheet properties
    # Getter
    @property
    def sheet(self) -> str:
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value: str):
        if value == '':
            raise ValueError('Breakdown sheet cannot be an empty string.')
        self._sheet = value
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Start cell properties
    # Getter
    @property
    def start_cell(self) -> str:
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value: str):
        # Try...
        try:
            # Get the cell's absolute indices
            self.start_column, self.start_row = self.get_cell_indices(value)
            # Set the starting cell
            self._start_cell = value
        # If an exception occurs...
        except Exception as e:
            raise ValueError(f'Passed start cell is not valid: {e}')
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        del self.start_row, self.start_column
        if self._mediator is not None:
            self._mediator.update_datasets()

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
            formula_template += f', {criteria[cell_or_range]}'

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
            # NOTE: IGNORES NONE
            unique_groups = [group for group in
                             table.data[group_by_column].unique()
                             if group is not None]

            # Sort the list of unique groups
            unique_groups.sort()

        # Create an empty 1D DataFrame using the unique groups
        self.data = DataFrame({group: [None] for group in unique_groups})

        # Create an index for the current header cell
        header_cell_index = 0

        # Get the start cell's absolute indices
        absolute_start_col, absolute_start_row = \
            self.get_cell_indices(self.start_cell)

        # For every group...
        for group in unique_groups:

            # Get the current header's column and row
            start_col = \
                get_column_letter(absolute_start_col + 1 + header_cell_index)
            start_row = \
                absolute_start_row + 1

            # Get the current header cell
            header_cell = f'{start_col}${start_row}'

            # Define the criteria dictionary
            criteria = {table.reference[group_by_column]['range']: header_cell}

            # Get a formula string
            formula_string = \
                self.create_conditional_aggregate_formula(table,
                                                          criteria,
                                                          summarize_column
                                                          )

            # Add the formula string to the current group entry
            self.data[group] = formula_string

            # Iterate the header cell index
            header_cell_index += 1

        # Set the breakdown cache
        self._breakdown_cache = {'function': self.create_1D,
                                 'arguments': {'table':
                                               table,
                                               'group_by_column':
                                               group_by_column,
                                               'summarize_column':
                                               summarize_column,
                                               'groups_to_summarize':
                                               groups_to_summarize}}

        return None

    # Method to create a two-dimensional breakdown
    def create_2D(self,
                  table: Table,
                  group_by_col_1: str,
                  group_by_col_2: str,
                  summarize_column: str,
                  groups_to_summarize: dict[str, list[str]] = None):

        # Create an empty dictionary to contain lists of unique groups
        unique_groups = {group_by_col_1: [], group_by_col_2: []}

        # If groups_to_summarize is not none...
        if groups_to_summarize is not None:

            # Get a list of booleans based on whether each key
            # in groups_to_summarize matches a group_by_col
            check_groups_list = [True if group_col in
                                 [group_by_col_1, group_by_col_2]
                                 else False for group_col in
                                 groups_to_summarize]

            # If groups to summarize is longer than two or contains a string
            # that is not equal to either column string...
            if len(groups_to_summarize) > 2 or not all(check_groups_list):

                # Raise an error
                raise ValueError('Unexpected keys in groups_to_summarize.')

            # Otherwise, pass
            else:
                pass

        # Create an empty dictionary if groups_to_summarize is None
        groups_to_summarize = \
            groups_to_summarize if groups_to_summarize is not None else {}

        # For every entry in unique_groups...
        for group_col in unique_groups:

            # If the group column is present in groups_to_summarize...
            if group_col in groups_to_summarize:

                # Set unique_groups[group_col] to a shallow
                # copy of groups_to_summarize entry
                unique_groups[group_col] = groups_to_summarize[group_col][:]

            # Otherwise...
            else:
                # Set unique_groups[group_col] to a list of unique values
                # in the group by column
                unique_groups[group_col] = [group for group in
                                            table.data[group_col].unique()
                                            if group is not None]

                # Sort the list
                unique_groups[group_col].sort()

        # Create a new column for group_2 (row headers)
        self.data[group_by_col_2] = \
            [group for group in unique_groups[group_by_col_2]]

        # Get the start cell's absolute indices
        absolute_start_col, absolute_start_row = \
            self.get_cell_indices(self.start_cell)

        # Create column index to track current column
        column_index = 0

        # For every group in unique_groups group_by_1 (treat as columns)...
        for group_1 in unique_groups[group_by_col_1]:

            # Get the current column header's column and row
            column_start_col = \
                get_column_letter(absolute_start_col + 2 +
                                  column_index)
            column_start_row = \
                absolute_start_row + 2

            # Get the current column header cell
            column_header_cell = f'{column_start_col}${column_start_row}'

            # Create row index to track current row
            row_index = 0

            # For every group in unique_groups group_by_2 (treat as rows)...
            for group_2 in unique_groups[group_by_col_2]:

                # Get the current row header's column and row
                row_start_col = \
                    get_column_letter(absolute_start_col + 1)
                row_start_row = \
                    absolute_start_row + 3 + row_index

                # Get the current row header cell
                row_header_cell = f'${row_start_col}{row_start_row}'

                # Define the criteria dictionary
                criteria = {table.reference[group_by_col_1]['range']:
                            column_header_cell,
                            table.reference[group_by_col_2]['range']:
                            row_header_cell}

                # Get a formula string
                formula_string = \
                    self.create_conditional_aggregate_formula(table,
                                                              criteria,
                                                              summarize_column
                                                              )

                # Add the formula string to the current group entry
                self.data.at[row_index, group_1] = formula_string

                # Iterate the row cell index
                row_index += 1

            # Iterate the header cell index
            column_index += 1

        # Set the breakdown cache
        self._breakdown_cache = {'function': self.create_1D,
                                 'arguments': {'table':
                                               table,
                                               'group_by_col_1':
                                               group_by_col_1,
                                               'group_by_col_2':
                                               group_by_col_2,
                                               'summarize_column':
                                               summarize_column,
                                               'groups_to_summarize':
                                               groups_to_summarize}}

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
