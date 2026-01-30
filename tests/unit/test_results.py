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

UNIT TESTING FOR RESULTS

Julia Hancock
Started 01-23-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestResults:

    # Test adding Tables to Results
    def test_add_table(self):

        # Create test result
        test_result = False
        # Create an instance of Results
        SomeResults = cq.Results()
        # Create a Table
        SomeTable = cq.Table()

        # Add the Table to Results
        SomeResults.add_table(SomeTable)

        # Check if the Table in Results is the same as original Table
        for table in SomeResults.tables:
            if table.id == SomeTable.id:
                if table == SomeTable:
                    test_result = True
                else:
                    pass
            else:
                pass

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
        SomeResults.add_value(SomeValue)

        # Check if the Value in Results is the same as original Value
        for value in SomeResults.values:
            if value.id == SomeValue.id:
                if value == SomeValue:
                    test_result = True
                else:
                    pass
            else:
                pass

        # If it is not, pass
        else:
            pass

        assert test_result

    # Test adding Formulas to Results
    def test_add_formula(self):

        # Create test result
        test_result = False

        # Create expected formula
        expected_formula = "=SUM('Some Sheet'!$C$5:$C$7)*'Some Sheet'!$B$3"

        # Create an instance of Results
        SomeResults = cq.Results()

        # Create a Table
        SomeTable = cq.Table(sheet='Some Sheet', start_cell='B4')
        # Add data to Table
        SomeTable.data['A'] = [1, 2, 3]
        SomeTable.data['B'] = [4, 5, 6]
        # Create a Value
        SomeValue = cq.Value(20, sheet='Some Sheet', start_cell='B2')

        # Add Table to Results
        SomeResults.add_table(SomeTable)
        # Add Value to Results
        SomeResults.add_value(SomeValue)

        # Create a new formula string
        new_formula_string = \
            (f'=SUM(|table: {SomeTable.id}, key: B, range: true|)'
             f'*|key: {SomeValue.id}|')

        # Create a Formula
        SomeFormula = \
            cq.Formula(new_formula_string)

        # Add pointers to Formula
        SomeFormula.point_to('C', SomeTable)

        # Add the Formula to the Results
        SomeResults.add_formula(SomeFormula)

        # If the expected formula matches the new Results formula...
        for table in SomeResults.tables:
            if table.id == SomeTable.id:
                if table.data.at[0, 'C'] == expected_formula:
                    # Set the test_result to True
                    test_result = True
                else:
                    pass
            else:
                pass
        # Otherwise, pass
        else:
            pass

        assert test_result

    # Test getting inserts for Tables and Values
    def test_get_insert(self):

        # Create test result
        test_result = False

        # Create expected pointers
        expected_table = '|table: Some Table, key: Some Column|'
        expected_value = '|key: Some Value|'
        # Create an instance of Results
        SomeResults = cq.Results()

        # Create a Table
        SomeTable = cq.Table()

        # Add a column to the Table
        SomeTable.data['Some Column'] = [1, 2, 3]

        # Create a Value
        SomeValue = cq.Value()

        # Add Table to Results
        SomeResults.add_table(SomeTable)

        # Add Value to Results
        SomeResults.add_value(SomeValue)

        # Get pointers for the Table and Value
        table_pointer = SomeResults.get_insert('Some Column', 'Some Table')
        value_pointer = SomeResults.get_insert('Some Value')

        # Check that the pointers match expected
        if table_pointer == expected_table and value_pointer == expected_value:
            # If so, set test_result to True
            test_result = True
        # Otherwise, set test_result to False
        else:
            test_result = False

        assert test_result

    # Test reporting Results
    def test_report_results(self):

        # Create test result
        test_result = False

        # Try to do the following...
        try:
            # Create new Tables and Values
            TableOne = cq.Table(sheet='First Sheet', start_cell='C13')
            TableTwo = cq.Table(sheet='First Sheet', start_cell='$B$2')
            TableThree = cq.Table(sheet='Second Sheet', start_cell='B4')
            ValueOne = cq.Value(sheet='First Sheet', start_cell='$B$8')
            ValueTwo = cq.Value(sheet='Second Sheet', start_cell='B1')

            # Add data to new Tables and Values
            TableOne.data['A'] = [1, 2, 3]
            TableOne.data['B'] = [4, 5, 6]
            TableTwo.data['C'] = [7, 8, 9]
            TableTwo.data['D'] = [10, 11, 12]
            TableTwo.data['E'] = [13, 14, 15]
            TableThree.data['F'] = [16, 17, 18]
            ValueOne.data = 19
            ValueTwo.data = 20

            # Create new Results
            ResultsOne = cq.Results()

            # Add Tables and Values to Results
            ResultsOne.add_table(TableOne)
            ResultsOne.add_table(TableTwo)
            ResultsOne.add_table(TableThree)
            ResultsOne.add_value(ValueOne)
            ResultsOne.add_value(ValueTwo)

            # Report Results
            ResultsOne.report_results('./tests/unit/report.xlsx')

            # Set test_result to True
            test_result = True

        # If an Exception is raised...
        except Exception as e:
            raise Exception(f'A test report could not be generated: {e}')

        assert test_result
