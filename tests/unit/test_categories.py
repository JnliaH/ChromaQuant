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

UNIT TESTING FOR CATEGORIES

Julia Hancock
Started 2-02-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestCategories:

    # Test creating instance and simple functions
    def test_simple(self):

        # Get a list of test results
        test_result = [False, False, False, False]

        # Create a categories instance
        SomeCategories = cq.utils.Categories()

        # Set a list of keywords to a category name
        SomeCategories['Category 1'] = ['Option 1', 'Option 2']
        # Repeat for a new category
        SomeCategories['Category 2'] = ['Option 3']

        # Create a list of values to compare
        uncategorized_values = ['Option 1', 'Option 3', 'Option 4', 'Option 2']
        # Create a list of expected categories
        expected_categories = ['Category 1', 'Category 2', '', 'Category 1']

        # For every uncategorized value...
        for i in range(len(uncategorized_values)):

            # Get a category
            category = SomeCategories.IS_EQUAL(uncategorized_values[i])

            # Set the test result accordingly
            test_result[i] = \
                True if category == expected_categories[i] else False

        assert all(test_result)
