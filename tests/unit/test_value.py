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

UNIT TESTING FOR VALUE

Julia Hancock
Started 01-23-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestValue:

    # Test getters
    def test_property_getting(self):

        # Create test result
        test_result = False
        # Create a Value
        SomeValue = cq.Value()

        # Try to get property values
        try:
            reference = SomeValue.reference
            data = SomeValue.data
            sheet = SomeValue.sheet
            start_cell = SomeValue.start_cell
            # Clear variables
            del reference, data, sheet, start_cell
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
        # Create a Value
        SomeValue = cq.Value()

        # Try to set property values
        try:
            SomeValue.data = 10
            SomeValue.sheet = 'Some Sheet'
            SomeValue.start_cell = '$A$1'
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
        # Create a Value
        SomeValue = cq.Value(sheet='Some Sheet',
                             start_cell='A1')

        # Try to set property values
        try:
            del SomeValue.sheet
            del SomeValue.start_cell
            # Set test_result to True if above lines worked
            test_result = True

        # If exception, pass
        except Exception:
            pass

        # Assert that test_result is true
        assert test_result
