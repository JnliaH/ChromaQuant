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

UNIT TESTING FOR FORMULA

Julia Hancock
Started 01-22-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestFormula:

    # Test Formula class
    def test_formula(self):

        # Number of individual tests
        number_tests = 5

        """ EXPECTED TEST RESULTS """

        expected_insert_list_pointers = {'table': 'Some Table',
                                         'key': 'Some Key'}

        first_expected_result = ["='Some Sheet'!$A$2",
                                 "='Some Sheet'!$A$3",
                                 "='Some Sheet'!$A$4",
                                 "='Some Sheet'!$A$5",
                                 "='Some Sheet'!$A$6",
                                 "='Some Sheet'!$A$7",
                                 "='Some Sheet'!$A$8",
                                 "='Some Sheet'!$A$9",
                                 "='Some Sheet'!$A$10",
                                 "='Some Sheet'!$A$11"]

        second_expected_result = ["='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8",
                                  "='Some Sheet'!$A$2:$A$8"]

        third_expected_result = "='Some Other Sheet'!$A$2"
        fourth_expected_result = "='Some Sheet'!$A$2:$A$8"

        """ CONSTANTS FOR TESTING """

        # DataSet References
        dataset_references = {'Some Table':
                              {'Some Key': {'column_letter': 'A',
                                            'start_row': 2,
                                            'end_row': 11,
                                            'sheet': 'Some Sheet',
                                            'length': 10,
                                            'range':
                                            "'Some Sheet'!$A$2:$A$8"}},
                              'Some Value': {'column_letter': 'A',
                                             'row': 1,
                                             'sheet': 'Some Other Sheet',
                                             'name_cell':
                                             "'Some Other Sheet'!$A$1",
                                             'data_cell':
                                             "'Some Other Sheet'!$A$2"}}

        # First formula for table output
        first_table_formula = \
            '=|table: Some Table, key: Some Key, range: False|'
        # Second formula for table output
        second_table_formula = \
            '=|table: Some Table, key: Some Key, range: True|'
        # First formula for value output
        first_value_formula = \
            '=|key: Some Value|'
        # Second formula for value output
        second_value_formula = \
            '=|table: Some Table, key: Some Key|'

        # Pointer to table as output
        output_table_pointer = {'table': 'Some Table', 'key': 'Some Other Key'}
        # Pointer to value as output
        output_value_pointer = {'key': 'Some Other Value'}

        # List of tests containing formulas and pointers for each test
        test_list = [{'formula': first_table_formula,
                      'pointer': output_table_pointer,
                      'expected': first_expected_result},

                     {'formula': second_table_formula,
                      'pointer': output_table_pointer,
                      'expected': second_expected_result},

                     {'formula': first_value_formula,
                      'pointer': output_value_pointer,
                      'expected': third_expected_result},

                     {'formula': second_value_formula,
                      'pointer': output_value_pointer,
                      'expected': fourth_expected_result}]

        """ TESTING """

        # Initialize list of formulas
        # For every test...
        for test in test_list:
            # Initialize a formula object
            test_formula = cq.Formula()
            # Add pointers
            test_formula.key_pointer = test['pointer']['key']
            if 'table' in test['pointer']:
                test_formula.table_pointer = test['pointer']['table']
            # Add a formula
            test_formula.formula_string = test['formula']
            # Insert references into this formula
            test_formula.insert_references(dataset_references)
            # Get the referenced formula from the previous step
            test['result'] = test_formula.referenced_formulas

        """ CHECKING TEST RESULTS """

        # Get a test results list of length number of tests
        test_results = [False] * number_tests

        # Check if the test_formula pointers match expected after final test.
        # If so, add a True statement to the test results list
        if test_formula.insert_list[0]['pointers'] == \
           expected_insert_list_pointers:
            test_results[0] = True

        # Otherwise, pass
        else:
            raise ValueError('Test Formula pointers do not match expected.')

        # For every reference test...
        for i in range(len(test_list)):

            # Check if the referenced formulas match expected formulas
            # If so, add a True statement to the list
            if test_list[i]['result'] == test_list[i]['expected']:
                test_results[i+1] = True

            # Otherwise, pass
            else:
                pass

        # Get the final result as True if all tests passed, False otherwise
        final_result = all(test_results)

        assert final_result

    # Test using base formulas
    def test_base_formulas(self):

        # Create a test result
        test_result = False

        # Create an expected formula
        expected_formula = ("=(SUM('Some Sheet'!$A$2:$A$5)+"
                            "('Some Sheet'!$D$2/'Some Sheet'!$G$2))")

        # Create table and value inserts
        table_1_insert = \
            '|table: Some Table, key: Column 1, range: True|'
        table_2_insert = \
            '|table: Some Other Table, key: Column 1, range: False|'
        value_insert = '|key: Value 1|'

        # Create table and value references
        dataset_references = {'Some Table':
                              {'Column 1': {
                                'column_letter': 'A',
                                'start_row': 2,
                                'end_row': 5,
                                'sheet': 'Some Sheet',
                                'length': 4,
                                'range': "'Some Sheet'!$A$2:$A$5"}},
                              'Some Other Table':
                              {'Column 1': {
                                'column_letter': 'D',
                                'start_row': 2,
                                'end_row': 5,
                                'sheet': 'Some Sheet',
                                'length': 4,
                                'range': "'Some Sheet'!$D$2:$D$5"}},
                              'Value 1':
                              {'column_letter': 'G',
                               'row': 1,
                               'sheet': 'Some Sheet',
                               'name_cell': "'Some Sheet'!$G$1",
                               'data_cell': "'Some Sheet'!$G$2"}}

        # Create a formula string by wrapping the range insert in SUM()
        formula_sum_string = cq.formula.WRAP_FORMULA_STRING(table_1_insert,
                                                            'SUM')

        # Create a formula using binary division
        formula_division = \
            cq.formula.FORMULA_DIVISION(table_2_insert, value_insert)

        # Create a formula using addition to previous formula
        formula = cq.formula.FORMULA_ADDITION(formula_sum_string,
                                              formula_division.formula_string)

        # Add pointers to the formula
        formula.key_pointer = 'Column 2'
        formula.table_pointer = 'Some Other Table'
        # Insert references for formula
        formula.insert_references(dataset_references)

        # If the first referenced formula is equal to expected...
        if formula.referenced_formulas[0] == expected_formula:
            # Set the test result to True
            test_result = True

        # Otherwise, pass
        else:
            pass

        assert test_result
