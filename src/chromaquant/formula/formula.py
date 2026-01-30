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

CLASS DEFINITION FOR FORMULA

Julia Hancock
Started 01-07-2026

"""

import logging
import re
from typing import Any, TYPE_CHECKING
from ..logging_and_handling import setup_logger, setup_error_logging

if TYPE_CHECKING:
    from ..data import Table

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASSES """


# Define the formula class
class Formula:

    """ SPECIAL METHODS """
    # Initialize class
    def __init__(self,
                 formula: str = ''):
        """__init__ summary

        Parameters
        ----------
        formula : str
            Passed formula with or without inserts and pointers
        pointer: dict
            Dictionary with key and (optionally) table name where
            the formula will be located

        """

        # Extract the formula if passed
        if formula != '':
            self._formula = formula
            self.get_formula_cell_inserts()

        # Otherwise set to a default value
        else:
            self._formula = None

        # Get blank attributes for key and table pointers
        self.key_pointer = ''
        self.table_pointer = ''

    # Object representation method, allows for direct access to formula
    def __repr__(self):
        # Return formula string
        return self._formula

    """ PROPERTIES """
    # Formula properties
    # Formula getter
    @property
    def formula_string(self):
        return self._formula

    # Formula setter
    @formula_string.setter
    def formula_string(self, value):
        self._formula = value
        self.get_formula_cell_inserts()

    # Formula deleter
    @formula_string.deleter
    def formula_string(self):
        del self._formula
        del self.insert_list

    """ METHODS """
    # Method to set formula pointer values
    @error_logging
    def point_to(self,
                 key_or_column: str,
                 table: Table):

        # Set the key pointer
        self.key_pointer = key_or_column

        # Set the table pointer
        self.table_pointer = table.id

        return None

    # Method to get cases in a formula where cells need to be inserted
    @error_logging
    def get_formula_cell_inserts(self):

        # Initialize a list to contain parsed pipe contents
        insert_list = []

        # If the formula contains at least one pipe character...
        if '|' in self._formula:

            # Get the number of pipes in the formula
            pipe_count = self._formula.count('|')

            # If the number of pipes is divisible by two...
            if pipe_count % 2 == 0:

                # Get a list of every substring within pipes
                insert_list = [{'start': match.start(),
                                'end': match.end(),
                                'raw': match.group(),
                                'pipe': [],
                                'pointers': {}}
                               for match in re.finditer(r'\|(.*?)\|',
                                                        self._formula)]

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
                                             ' unexpected number of colons')

                    # Remove the pipe key-value pairs
                    del insert_list[i]['pipe']

            # Otherwise, raise an error
            else:
                raise ValueError('Formula contains at least'
                                 'one hanging pipe delimeter:'
                                 f' "{self._formula}"')

        # Otherwise, pass
        else:
            pass

        # Save the insert list to a class attribute
        self.insert_list = insert_list

        return None

    # Method to replace formula inserts with references
    @error_logging
    def insert_references(self,
                          dataset_references: dict[str, dict[Any]]):

        # Get a dataset references attribute
        self.dataset_references = dataset_references

        # If the insert list is not None (i.e., there are inserts)...
        if self.insert_list is not None:

            # If function was passed a table to output to...
            if self.table_pointer != '' and self.key_pointer != '':

                # Get the list of referenced formulas
                self.referenced_formulas = \
                    self.process_table_formula_inserts()

            # Otherwise, if the function was passed a value to output to...
            elif self.key_pointer != '':

                # Get the list of referenced formulas
                self.referenced_formulas = \
                    self.process_value_formula_inserts()

            # Otherwise, raise an error
            else:
                raise ValueError('Passed output pointers do not'
                                 ' point to either a value or table')

        return None

    # Method to process table formula inserts
    @error_logging
    def process_table_formula_inserts(self):
        """
        process_table_formula_inserts

        Parameters
        ----------
        None

        Returns
        -------
        new_formula : list or str
            New formula or list of new formulas.

        Raises
        ------
        ValueError
            'Insert list contains non-key or non-table elements'
        ValueError
            'Formula missing necessary keys'
        ValueError
            'Passed output pointers do not point to either a value or table'
        """

        # Try...
        try:

            # Get the table length
            # NOTE: USES THE LENGTH FROM THE FIRST COLUMN IN THE TABLE
            output_table_length = \
                self.dataset_references[
                    self.table_pointer
                    ][
                    next(iter(self.table_pointer[self.table_pointer]))
                    ]['length']

            # If length is less than one, set to five
            if output_table_length < 1:
                output_table_length = 5

            # Otherwise, pass
            else:
                pass

        # If can't get the length, set to five
        except Exception:
            logger.info('Formula output pointer indicates empty column.')
            output_table_length = 5

        # If there is at least one table among inserts...
        if any('table' in insert.get('pointers', {})
                and 'key' in insert.get('pointers', {})
                for insert in self.insert_list):

            # Get the length of the longest named table
            max_table_length = max(
                [self.dataset_references[
                    insert['pointers']['table']
                    ][
                    insert['pointers']['key']
                    ]['length']
                    for insert in self.insert_list
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
            new_formula = \
                [self._formula for i in range(output_table_length)]

            # For every insert...
            for insert in self.insert_list:

                # If the insert has a table and key pointer...
                if 'table' in insert['pointers'] \
                   and 'key' in insert['pointers']:

                    # Get the insert's table and key pointers
                    table_id = insert['pointers']['table']
                    column_name = insert['pointers']['key']

                    # Get the current table reference
                    table_ref = self.dataset_references[table_id]

                    # If the insert has range pointer equal to true...
                    if 'range' in insert['pointers'] and \
                        insert['pointers']['range'].capitalize() \
                       == 'True':

                        # Get a range substring for each
                        # new entry in the output table
                        insert['reference'] = \
                            table_ref[column_name]['range']

                        # Replace the insert's raw substring
                        # for every formula in the new formula list
                        new_formula = \
                            [self.replace_insert(one_formula,
                                                 insert['raw'],
                                                 insert['reference'])
                                for one_formula in new_formula]

                    # Otherwise...
                    else:

                        # Get the column letter
                        column_letter = \
                            table_ref[column_name]['column_letter']
                        # Get the column sheet
                        column_sheet = \
                            table_ref[column_name]['sheet']

                        # Get the start and end rows
                        start_row = \
                            table_ref[column_name]['start_row']
                        end_row = \
                            table_ref[column_name]['end_row']

                        # Get a list of insert references for each
                        # row iterated over, adjusted to ignore header
                        insert['reference'] = \
                            [
                                f"'{column_sheet}'!"
                                f"${column_letter}${row}"
                                for row in
                                range(start_row + 1, end_row + 2)
                                ]

                        # Replace the insert's raw substring
                        # for every formula in the new formula list
                        new_formula = \
                            [self.replace_insert(new_formula[i],
                                                 insert['raw'],
                                                 insert['reference'][i]
                                                 )
                                for i in range(output_table_length)]

                # Otherwise, if the insert has a key pointer...
                elif 'key' in insert['pointers']:

                    # Get the key pointer
                    key_id = insert['pointers']['key']

                    # Get the value's data reference string
                    insert['reference'] = \
                        self.dataset_references[key_id]['data_cell']

                    # Replace the insert's raw substring
                    # for every formula in the new formula list
                    new_formula = \
                        [self.replace_insert(one_formula,
                                             insert['raw'],
                                             insert['reference'])
                            for one_formula in new_formula]

                # Otherwise, raise an error
                else:
                    raise ValueError('Insert list contains '
                                     'non-key or non-table elements')

        # Otherwise, if there are only values among inserts...
        elif all('key' in insert.get('pointers', {})
                 for insert in self.insert_list):

            # Initialize a new formula list
            new_formula = \
                [self._formula for i in range(output_table_length)]

            # Initialize a string formula to use in iterations
            iterate_formula = self._formula

            # For every insert...
            for insert in self.insert_list:

                # Get the key pointer
                key_id = insert['pointers']['key']

                # Get the value's reference string
                insert['reference'] = \
                    self.dataset_references[key_id]['data_cell']

                # Replace insert substring with value's reference
                iterate_formula = \
                    self.replace_insert(iterate_formula,
                                        insert['raw'],
                                        insert['reference'])

            # Set the new formula list to be iterate_formula for
            # every entry in the output_table's column
            new_formula = [iterate_formula
                           for row in range(output_table_length)]

        # Otherwise, raise an exception
        else:
            raise ValueError(
                'Insert list contains non-key or non-table elements'
            )

        return new_formula

    # Method to process value formula inserts
    @error_logging
    def process_value_formula_inserts(self):
        """
        process_value_formula_inserts

        Parameters
        ----------
        None

        Returns
        -------
        new_formula : str
            New formula.

        Raises
        ------
        ValueError
            'Formula missing necessary keys'
        """

        # Initialize a new formula
        new_formula = self._formula

        # For every insert...
        for insert in self.insert_list:

            # If the insert has a table and key pointer...
            if 'table' in insert['pointers'] \
               and 'key' in insert['pointers']:

                # Get the insert's table and key pointers
                table_id = insert['pointers']['table']
                column_name = insert['pointers']['key']

                # Get the table reference
                table_ref = self.dataset_references[table_id]

                # Get a range substring and save to insert['reference']
                insert['reference'] = \
                    table_ref[column_name]['range']

                # Replace pointer substring with range substring
                new_formula = \
                    new_formula.replace(
                        insert['raw'],
                        insert['reference'])

            # Otherwise, if insert has a key pointer...
            elif 'key' in insert['pointers']:

                # Get the key pointer
                key_id = insert['pointers']['key']

                # Get the value's reference string
                insert['reference'] = \
                    self.dataset_references[key_id]['data_cell']

                # Replace insert substring with value's reference
                new_formula = \
                    self.replace_insert(new_formula,
                                        insert['raw'],
                                        insert['reference'])

            # Otherwise, raise an error
            else:
                raise ValueError('Formula missing necessary keys')

        return new_formula

    """ STATIC METHODS """
    # Method to replace formula raw insert with reference
    @staticmethod
    def replace_insert(formula, raw, reference):

        # Replace pointer substring with value's reference
        new_formula = \
            formula.replace(raw, reference)

        return new_formula
