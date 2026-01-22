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
from ..logging_and_handling import setup_logger, setup_error_logging

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

    # Initialize class
    def __init__(self, formula):
        """
        __init__

        Parameters
        ----------
        formula : str
            Passed formula with or without inserts and pointers

        """

        # Extract the formula
        self.formula = formula

        # Get the formula's cell inserts
        self.get_formula_cell_inserts()

    """ METHODS """

    # Function to get cases in a formula where cells need to be inserted
    @error_logging
    def get_formula_cell_inserts(self):

        # Initialize a list to contain parsed pipe contents
        insert_list = []

        # If the formula contains at least one pipe character...
        if '|' in self.formula:

            # Get the number of pipes in the formula
            pipe_count = self.formula.count('|')

            # If the number of pipes is divisible by two...
            if pipe_count % 2 == 0:

                # Get a list of every substring within pipes
                insert_list = [{'start': match.start(),
                                'end': match.end(),
                                'raw': match.group(),
                                'pipe': [],
                                'pointers': {}}
                               for match in re.finditer(r'\|(.*?)\|',
                                                        self.formula)]

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

            # Otherwise, raise an error
            else:
                raise ValueError('Formula contains at least'
                                 'one hanging pipe delimeter:'
                                 f' "{self.formula}"')

        # Otherwise, pass
        else:
            pass

        # Save the insert list to a class attribute
        self.insert_list = insert_list

        return None

    # Function to process table formula inserts
    @error_logging
    def process_table_formula_inserts(self,
                                      value_references,
                                      table_references,
                                      output_pointers):
        """
        process_table_formula_inserts

        Parameters
        ----------
        value_references : dict
            Dictionary of headers by value name.
        table_references : dict
            Dictionary of headers by table name.
        output_pointers : _type_
            Pointer(s) to where new formulas will go.

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

        # If the insert list is not None (i.e., there are inserts)...
        if self.insert_list is not None:

            # If function was passed a table to output to...
            if 'table' in output_pointers \
                 and 'key' in output_pointers:

                # Try...
                try:

                    # Get the table pointer
                    table_pointer = output_pointers['table']
                    # Get the table length
                    output_table_length = \
                        table_references[table_pointer][
                            next(iter(table_references[table_pointer]))
                            ]['length']

                    # If length is less than one, set to five
                    if output_table_length < 1:
                        output_table_length = 5

                    # Otherwise, pass
                    else:
                        pass

                # If can't get the length, set to five
                except KeyError:
                    output_table_length = 5

                # If there is at least one table among inserts...
                if any('table' in insert.get('pointers', {})
                       and 'key' in insert.get('pointers', {})
                       for insert in self.insert_list):

                    # Get the length of the longest named table
                    max_table_length = max(
                        [table_references[
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
                        [self.formula for i in range(output_table_length)]

                    # For every insert...
                    for insert in self.insert_list:

                        # If the insert has a table and key pointer...
                        if 'table' in insert['pointers'] \
                           and 'key' in insert['pointers']:

                            # Get the insert's table and key pointers
                            table_name = insert['pointers']['table']
                            column_name = insert['pointers']['key']

                            # Get the current table reference
                            table_ref = table_references[table_name]

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
                                print(table_ref)

                                # Get the start and end rows
                                start_row = \
                                    table_ref[column_name]['start_row']
                                end_row = \
                                    table_ref[column_name]['end_row']

                                # Get a list of insert references for each
                                # row iterated over
                                insert['reference'] = \
                                    [
                                        f"'{column_sheet}'!"
                                        f"${column_letter}${row}"
                                        for row in
                                        range(start_row, end_row + 1)
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
                            key_pointer = insert['pointers']['key']

                            # Get the value's reference string
                            insert['reference'] = \
                                value_references[key_pointer]['cell']

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
                        [self.formula for i in range(output_table_length)]

                    # Initialize a string formula to use in iterations
                    iterate_formula = self.formula

                    # For every insert...
                    for insert in self.insert_list:

                        # Get the key pointer
                        key_pointer = insert['pointers']['key']

                        # Get the value's reference string
                        insert['reference'] = \
                            value_references[key_pointer]['cell']

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

            # Otherwise, raise an error
            else:
                raise ValueError('Passed output pointers do not'
                                 ' point to either a value or table')

        # Otherwise, pass
        else:
            pass

        # Set the new formula attribute to the result
        self.new_formula = new_formula

        return None

    # Function to process value formula inserts
    @error_logging
    def process_value_formula_inserts(self,
                                      value_references: dict[str, dict],
                                      table_references: dict[str, dict]
                                      ):
        """
        process_value_formula_inserts

        Parameters
        ----------
        value_references : dict
            Dictionary of references by value name.
        table_references : dict
            Dictionary of references by table name.

        Returns
        -------
        new_formula : list or str
            New formula or list of new formulas.

        Raises
        ------
        ValueError
            'Formula missing necessary keys'
        """

        # Initialize a new formula
        new_formula = self.formula

        # For every insert...
        for insert in self.insert_list:

            # If the insert has a table and key pointer...
            if 'table' in insert['pointers'] \
               and 'key' in insert['pointers']:

                # Get the insert's table and key pointers
                table_name = insert['pointers']['table']
                column_name = insert['pointers']['key']

                # Get the table reference
                table_ref = table_references[table_name]

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
                key_pointer = insert['pointers']['key']

                # Get the value's reference string
                insert['reference'] = \
                    value_references[key_pointer]['cell']

                # Replace insert substring with value's reference
                new_formula = \
                    self.replace_insert(new_formula,
                                        insert['raw'],
                                        insert['reference'])

            # Otherwise, raise an error
            else:
                raise ValueError('Formula missing necessary keys')

        return None

    """ STATIC METHODS """
    # Method to replace formula raw insert with reference
    @staticmethod
    def replace_insert(formula, raw, reference):

        # Replace pointer substring with value's reference
        new_formula = \
            formula.replace(raw, reference)

        return new_formula
