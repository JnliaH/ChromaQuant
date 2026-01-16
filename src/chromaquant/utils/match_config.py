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

CLASS DEFINITION FOR TABLES

Julia Hancock
Started 01-12-2025

"""

import logging
#from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
#logger = setup_logger(logger)

# Get an error logging decorator
#error_logging = setup_error_logging(logger)

""" CLASS """

# Define ConfigProperty class
class ConfigProperty():

    # Descriptor __set_name__
    def __set_name__(self, owner, name):
        self.name = '_' + name
    
    # Getter
    def __get__(self, obj, type=None):
        return getattr(obj, self.name)

    # Setter
    def __set__(self, obj, value):
        setattr(obj, self.name, value)

    # Deleter
    def __delete__(self, obj):
        delattr(obj, self.name)

# Define MatchConfig class
class MatchConfig():

    # Create class instances of ConfigProperty for every property
    do_export = ConfigProperty()
    import_include_col = ConfigProperty()
    local_filter_row = ConfigProperty()
    match_comparison_function = ConfigProperty()
    match_comparison_error = ConfigProperty()
    output_cols_dict = ConfigProperty()
    output_path = ConfigProperty()
    output_rename_dict = ConfigProperty()

    # Initialize
    def __init__(self):

        # Define default match comparison function
        def default_comp_function(x):
            return x

        # Set default descriptor values
        self.do_export = False
        self.import_include_col = {}
        self.local_filter_row = {}
        self.match_comparison_function = default_comp_function
        self.match_comparison_error = 0
        self.output_cols_dict = {}
        self.output_path = 'match_results.csv'
        self.output_rename_dict = {}
