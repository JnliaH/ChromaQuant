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
Started 01-23-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestResults():

    # Test adding Tables to Results
    def test_add_table(self):

        # Create test result
        test_result = False
        # Create an instance of Results
        SomeResults = cq.Results()
        # Create a Table
        SomeTable = cq.Table()

        # Add the Table to Results
        SomeResults.add_table(SomeTable, 'Some Table')

        # Check if the Table in Results is the same as original Table
        if SomeResults.tables['Some Table'] == SomeTable:
            test_result = True

        # If it is not, pass
        else:
            pass

        assert test_result

    # Test adding Values to Results
    def test_add_value(self):

        # Create test result
        test_result = False
        # Create an instance of Results
        SomeResults = cq.Results()
        # Create a Value
        SomeValue = cq.Value(10)

        # Add the Value to Results
        SomeResults.add_value(SomeValue, 'Some Value')

        # Check if the Table in Results is the same as original Table
        if SomeResults.values['Some Value'].data == SomeValue.data:
            test_result = True

        # If it is not, pass
        else:
            pass

        assert test_result

    # Test adding Formulas to Results
    def test_add_formula(self):

        # Create test result
        test_result = False

        # Create expected formula
        expected_formula = "=SUM('Some Sheet'!$C$5:$C$7)*'Some Sheet'!$B$2"

        # Create an instance of Results
        SomeResults = cq.Results()

        # Create a Table
        SomeTable = cq.Table(sheet='Some Sheet', start_cell='B4')
        # Add data to Table
        # TODO: FIND A WAY TO ALLOW FOR DIRECT ASSIGNMENT USING PANDAS LOGIC
        # THAT DOES NOT BYPASS THE SETTER
        SomeTable.add_table_column('A', [1, 2, 3])
        SomeTable.add_table_column('B', [4, 5, 6])
        # Create a Value
        SomeValue = cq.Value(20, sheet='Some Sheet', start_cell='B2')

        # Add Table to Results
        SomeResults.add_table(SomeTable, 'Some Table')
        # Add Value to Results
        SomeResults.add_value(SomeValue, 'Some Value')

        # Create a pointer for a new formula
        new_formula_pointer = {'table': 'Some Table', 'key': 'C'}
        # Create a new formula string
        new_formula_string = \
            '=SUM(|table: Some Table, key: B, range: true|)*|key: Some Value|'

        # Create a Formula
        SomeFormula = \
            cq.Formula(new_formula_string, new_formula_pointer)

        # Add the Formula to the Results
        SomeResults.add_formula(SomeFormula)

        # If the expected formula matches the new Results formula...
        if SomeResults.tables['Some Table'].data.at[0, 'C'] \
           == expected_formula:
            # Set the test_result to True
            test_result = True
        # Otherwise, pass
        else:
            pass

        assert test_result
