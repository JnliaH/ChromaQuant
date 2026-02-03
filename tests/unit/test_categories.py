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
Started 02-02-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestCategories:

    # Test creating instance and simple functions
    def test_creation_attributes(self):

        # Get a test result
        test_result = False

        # Create a categories instance
        SomeCategories = cq.utils.Categories()

        # Set the test result to True after all testing
        test_result = True

        assert test_result

print('done')