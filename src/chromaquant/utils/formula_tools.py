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

COLLECTION OF VARIOUS FORMULA TOOLS

Julia Hancock
Started 1-07-2026

"""

import re
from openpyxl.utils import get_column_letter, coordinate_to_tuple

""" FUNCTIONS """


# Function for checking that passed formula starts with '='
def check_formula_starts_with_equals(formula):

    # Initialize tf
    tf = False

    # If a match exists, set tf to True
    if not re.search('^=', formula) is None:
        tf = True
    # Otherwise, pass
    else:
        pass

    return tf


# Function to get a column letter based on table
# starting column and column's index within a table
def get_column_letter_from_table(
        table_reference, column_name, start_cell_column):

    # Find the column's index within the DataFrame
    column_index = \
        table_reference['columns'].index(column_name)

    # Add the column's index to the starting column
    # and get the column letter equivalent
    column_letter = \
        get_column_letter(start_cell_column + column_index)

    return column_letter


# Function to construct value reference string
def get_value_reference_string(value_reference):

    # Get value's sheet string
    value_sheet = \
        f"'{value_reference['sheet']}'!"
    # Get value's cell string
    value_cell = \
        f"{value_reference['cell']}"

    # Get the reference string
    reference = value_sheet + value_cell

    return reference


# Function to get the starting row and column of a table
def get_table_start_coords(table_reference):

    # Get the table's starting cell
    table_start_cell = table_reference['start_cell']

    # Get the starting cell's row and column
    start_row, start_column = \
        coordinate_to_tuple(table_start_cell)

    return start_row, start_column


# Function to replace formula raw insert with reference
def replace_insert(formula, raw, reference):

    # Replace pointer substring with value's reference
    new_formula = \
        formula.replace(raw, reference)

    return new_formula


# Function to get a range from passed table pointers
def table_column_to_range(table_reference, column_key):

    # Get the starting coordinates
    start_row, start_column = get_table_start_coords(table_reference)

    # Get letter for output column
    column_letter = \
        get_column_letter_from_table(table_reference, column_key, start_column)

    # Get the final row of the table
    end_row = start_row + table_reference['length']

    # Construct the range string
    column_range = (
        f'${column_letter}${start_row + 1}:'
        f'${column_letter}${end_row + 1}')

    return column_range
