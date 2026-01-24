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

UNIT TESTING FOR TABLE

Julia Hancock
Started 01-22-2026

"""

import chromaquant as cq
import pandas as pd

""" TEST CLASS """


class TestTable:

    # Test ability to use Table getters
    def test_property_getting(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()

        # Try to get property values
        try:
            references = SomeTable.references
            data = SomeTable.data
            sheet = SomeTable.sheet
            start_cell = SomeTable.start_cell
            # Clear variables
            del references, data, sheet, start_cell
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result

    # Test ability to use Table setters
    def test_property_setting(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()

        # Try to set property values
        try:
            SomeTable.data = pd.DataFrame()
            SomeTable.sheet = 'Some Sheet'
            SomeTable.start_cell = '$A$1'
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result

    # Test ability to use Table deleters
    def test_property_deleting(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()

        # Try to set property values
        try:
            del SomeTable.sheet
            del SomeTable.start_cell
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result

    # Test ability to add new column with value
    def test_new_column_value(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()

        # Try to set property values
        try:
            SomeTable.add_table_column('New Column', 4)
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result

    # Test ability to add new column with iterable
    def test_new_column_iterate(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()

        # Try to set property values
        try:
            SomeTable.add_table_column('New Column', [1, 2, 3])
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result

    # Test ability to import .csv data
    def test_import_csv_data(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()

        # Try to set property values
        try:
            SomeTable.import_csv_data('./tests/unit/table_data.csv')
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result

    # Test matching method
    def test_match(self):

        # Create test result
        test_result = False
        # Create a table
        SomeTable = cq.Table()
        # Get data for matching
        data_to_match = pd.read_csv('./tests/unit/data_to_match.csv')
        # Import data
        SomeTable.import_csv_data('./tests/unit/table_data.csv')
        # Create expected match_data
        expected_match_data = pd.DataFrame({'A': [1, 2, 3],
                                            'B': [4, 5, 6],
                                            'C': [7, 8, 9]})
        # Try to run matching
        try:
            # Create match configuration
            match_config = cq.MatchConfig()
            # Add match condition
            match_config.add_match_condition(match_config.IS_EQUAL,
                                             'A')
            # Run match function
            match_data = SomeTable.match(data_to_match, match_config)
            # Force column to be type string
            # TODO: FIND SOURCE OF THIS TYPEING ISSUE
            match_data['C'] = match_data['C'].astype(int)

            # If match data matches expected...
            if match_data.equals(expected_match_data.sort_index(axis=1)):
                # Set test result to True
                test_result = True

            # Otherwise, pass
            else:
                pass

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result
