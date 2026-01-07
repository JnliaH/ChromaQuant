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

import pandas as pd
import re
from openpyxl.utils import get_column_letter, coordinate_to_tuple
from .. import import_local_packages as ilp
from .. import logging_and_handling as lah

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
mt = ilp.import_from_path("mt", subpack_dir['Match'])
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
            # Create a new table entry in the tables dictionary
            self.tables[table_name] = {'type': 'table',
                                       'sheet': sheet,
                                       'start_cell': start_cell,
                                       'data': data_frame,
                                       'length': len(data_frame)}
        # Otherwise, raise error
        else:
            raise ValueError(f'Starting cell "{start_cell}" is not valid')
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
            self.values[value_name] = {'type': 'value',
                                       'sheet': sheet,
                                       'cell': cell,
                                       'data': data}
        # Otherwise, raise error
        else:
            raise ValueError(f'Cell "{cell}" is not valid')

        return None

    # Function to add a new column to a table
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

    # Function for checking that passed formula starts with '='
    @staticmethod
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

    # Function to get cases in a formula where cells need to be inserted
    @staticmethod
    @error_logging
    def get_formula_cell_inserts(formula):

        # Initialize a list to contain parsed pipe contents
        insert_list = []

        # If the formula contains at least one pipe character...
        if '|' in formula:

            # Get the number of pipes in the formula
            pipe_count = formula.count('|')

            # If the number of pipes is divisible by two...
            if pipe_count % 2 == 0:

                # Get a list of every substring within pipes
                insert_list = [{'start': match.start(),
                                'end': match.end(),
                                'raw': match.group(),
                                'pipe': [],
                                'pointers': {}}
                               for match in re.finditer(r'\|(.*?)\|', formula)]

                # For each pipe substring...
                for i in range(len(insert_list)):

                    # Split each substring if it contains commas
                    insert_list[i]['pipe'] = \
                        insert_list[i]['raw'].split(',')

                    # For each newly-split substring...
                    for j in range(len(insert_list[i]['pipe'])):

                        # If the substring contains one colon...
                        if insert_list[i]['pipe'][j].count(':') == 1:

                            # Split the substring by that colon
                            key_value_list = \
                                insert_list[i]['pipe'][j].split(':')

                            # Strip the key and value of pipes and whitespace
                            key_value_list = \
                                [k.strip('|').strip() for k in key_value_list]

                            # Add the key-value pair to the pointers dictionary
                            insert_list[i]['pointers'][key_value_list[0]] = \
                                key_value_list[1]

                        # Otherwise, raise error
                        else:
                            raise ValueError('At least one pointer contains an'
                                             'unexpected number of colons')

                    # Remove the pipe key-value pairs
                    del insert_list[i]['pipe']

                return insert_list

            # Otherwise, raise an error
            else:
                raise ValueError('Formula contains at least'
                                 'one hanging pipe delimeter:'
                                 f' "{formula}"')

        # Otherwise, pass
        else:
            pass

        return None

    # Function to process formula inserts
    @error_logging
    def process_formula_inserts(self, formula, output_pointers):

        # Function to get the starting row and column of a table
        def get_table_start_coords(table):

            # Get the table's starting cell
            table_start_cell = table['start_cell']

            # Get the starting cell's row and column
            start_row, start_column = \
                coordinate_to_tuple(table_start_cell)

            return start_row, start_column

        # Function to get a column letter based on table
        # starting column and column's index within a table
        def get_column_letter_from_table(
                table, column_name, start_cell_column):

            # Find the column's index within the DataFrame
            column_index = \
                table['data'].columns.get_loc(column_name)

            # Add the column's index to the starting column
            # and get the column letter equivalent
            column_letter = \
                get_column_letter(start_cell_column + column_index)

            return column_letter

        # Function to get a range from passed table pointers
        def table_column_to_range(table, column_key):

            # Get the starting coordinates
            start_row, start_column = get_table_start_coords(table)

            # Get letter for output column
            column_letter = \
                get_column_letter_from_table(table, column_key, start_column)

            # Get the final row of the table
            end_row = start_row + table['length']

            # Construct the range string
            column_range = (
                f'${column_letter}${start_row + 1}:'
                f'${column_letter}${end_row + 1}')

            return column_range

        # Function to construct value reference string
        def get_value_reference_string(self, insert):

            # Get value's sheet string
            value_sheet = \
                f"'{self.values[
                    insert['pointers']['key']
                    ]['sheet']}'!"
            # Get value's cell string
            value_cell = \
                f"{self.values[
                    insert['pointers']['key']
                    ]['cell']}"

            # Get the reference string
            reference = value_sheet + value_cell

            return reference

        # Function to replace formula raw insert with reference
        def replace_insert(formula, raw, reference):

            # Replace pointer substring with value's reference
            new_formula = \
                formula.replace(raw, reference)

            return new_formula

        # Find cell inserts within formula
        # This function also checks whether open pipes have closing pipes
        insert_list = self.get_formula_cell_inserts(formula)

        # If the insert list is not None (i.e., there are inserts)
        if insert_list is not None:

            # If function was passed a table to output to
            if 'table' in output_pointers \
                 and 'key' in output_pointers:

                # Try to get the output table length:
                try:
                    output_table_length = \
                        len(self.tables[output_pointers['table']]['data'])

                # If can't get the length, set to five
                except KeyError:
                    output_table_length = 5

                # If there is at least one table among inserts...
                if any('table' in insert.get('pointers', {})
                       and 'key' in insert.get('pointers', {})
                       for insert in insert_list):

                    # Get the length of the longest named table
                    max_table_length = max(
                        [len(self.tables[
                            insert['pointers']['table']
                            ]['data'])
                            for insert in insert_list
                            if 'table' in insert.get('pointers', {})]
                    )

                    # If the max_table_length is greater than 1, set
                    # the output_table_length to the max_table_length
                    if max_table_length > 1:
                        output_table_length = max_table_length

                    # Otherwise, pass
                    else:
                        pass

                    # Initialize a new formula list
                    new_formula = [formula for i in range(output_table_length)]

                    # For every insert...
                    for insert in insert_list:

                        # If the insert has a table and key pointer...
                        if 'table' in insert['pointers'] \
                           and 'key' in insert['pointers']:

                            # Get the insert's table and key pointers
                            table_name = insert['pointers']['table']
                            column_name = insert['pointers']['key']

                            # Get the table from the tables object
                            insert_table = self.tables[table_name]

                            # If the insert has range pointer equal to true...
                            if 'range' in insert['pointers'] and \
                               insert['pointers']['range'].capitalize() \
                               == 'True':

                                # Get a range substring for each
                                # new entry in the output table
                                insert['reference'] = \
                                    table_column_to_range(insert_table,
                                                          column_name)

                                # Replace the insert's raw substring
                                # for every formula in the new formula list
                                new_formula = \
                                    [replace_insert(one_formula,
                                                    insert['raw'],
                                                    insert['reference'])
                                     for one_formula in new_formula]

                            # Otherwise...
                            else:

                                # Get the table's starting coordinates
                                start_row, start_column = \
                                    get_table_start_coords(insert_table)

                                # Get letter for output column
                                column_letter = \
                                    get_column_letter_from_table(
                                        insert_table,
                                        column_name,
                                        start_column)

                                # Get a list of insert references for each
                                # row iterated over
                                insert['reference'] = \
                                    [f'{column_letter}{row}' for row in
                                     range(start_row + 1,
                                           start_row + output_table_length + 1)
                                     ]

                                # Replace the insert's raw substring
                                # for every formula in the new formula list
                                new_formula = \
                                    [replace_insert(new_formula[i],
                                                    insert['raw'],
                                                    insert['reference'][i])
                                     for i in range(output_table_length)]

                        # Otherwise, if the insert has a key pointer...
                        elif 'key' in insert['pointers']:

                            # Get the value's reference string
                            insert['reference'] = \
                                get_value_reference_string(self, insert)

                            # Replace the insert's raw substring
                            # for every formula in the new formula list
                            new_formula = \
                                [replace_insert(one_formula,
                                                insert['raw'],
                                                insert['reference'])
                                    for one_formula in new_formula]

                        # Otherwise, raise an error
                        else:
                            raise ValueError('Insert list contains '
                                             'non-key or non-table elements')

                # Otherwise, if there are only values among inserts...
                elif all('key' in insert.get('pointers', {})
                         for insert in insert_list):

                    # Initialize a new formula list
                    new_formula = [formula for i in range(output_table_length)]

                    # Initialize a string formula to use in iterations
                    iterate_formula = formula

                    # For every insert...
                    for insert in insert_list:

                        # Get the value's reference string
                        insert['reference'] = \
                            get_value_reference_string(self, insert)

                        # Replace insert substring with value's reference
                        iterate_formula = \
                            replace_insert(iterate_formula,
                                           insert['raw'],
                                           insert['reference'])

                    # Set the new formula list to be iterate_formula for
                    # every entry in the output_table's column
                    new_formula = [iterate_formula
                                   for row in range(output_table_length)]

                # Otherwise, raise an exception
                else:
                    raise ValueError(
                        'Insert list contains non-key or non-table elements')

            # If function was passed a value to output to...
            elif 'key' in output_pointers:

                # Initialize a new formula
                new_formula = formula

                # For every insert...
                for insert in insert_list:

                    # If the insert has a table and key pointer...
                    if 'table' in insert['pointers'] \
                       and 'key' in insert['pointers']:

                        # Get the insert's table and key pointers
                        table_name = insert['pointers']['table']
                        column_name = insert['pointers']['key']

                        # Get the table from the tables object
                        insert_table = self.tables[table_name]

                        # Get a range substring and save to insert['reference']
                        insert['reference'] = \
                            table_column_to_range(insert_table, column_name)

                        # Replace pointer substring with range substring
                        new_formula = \
                            new_formula.replace(
                                insert['raw'],
                                insert['reference'])

                    # Otherwise, if insert has a key pointer...
                    elif 'key' in insert['pointers']:

                        # Get the value's reference string
                        insert['reference'] = \
                            get_value_reference_string(self, insert)

                        # Replace insert substring with value's reference
                        new_formula = \
                            replace_insert(new_formula,
                                           insert['raw'],
                                           insert['reference'])

                    # Otherwise, raise an error
                    else:
                        raise ValueError('Formula missing necessary keys')

            # Otherwise, raise an error
            else:
                raise ValueError('Passed output pointers do not'
                                 ' point to either a value or table')

        # Otherwise, pass
        else:
            pass

        return new_formula

    # Function to add a new Excel formula to a cell or table
    def add_new_formula(self, formula, value_or_column_name, table=''):

        # Create a pointers dictionary with the value or column name
        pointers = {'key': value_or_column_name}

        # If passed an output table string...
        if table != '':
            # Add a table key-value pair to pointers
            pointers['table'] = table

        # Otherwise, pass

        # Get a new formula or list of new formulas
        new_formula = self.process_formula_inserts(formula, pointers)

        # If there was no table string...
        if table == '':

            # Set the corresponding value in the values object to new_formula
            self.values[value_or_column_name] = new_formula

        # Otherwise...
        else:

            # Set the corresponding column in the table to new_formula
            self.tables[table]['data'][value_or_column_name] = new_formula

        return None
