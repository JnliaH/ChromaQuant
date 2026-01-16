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
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define MatchConfig class
class MatchConfig():

    # Initialization function
    def __init__(self):

        # Define default match comparison function
        def default_comp_function(x):
            return x

        # Define default MatchConfig attributes
        self._do_export = False
        self._output_path = 'match_results.csv'
        self._local_filter_row = {}
        self._output_rename_dict = {}
        self._output_cols_dict = {}
        self._import_include_col = []
        self._match_comparison_function = default_comp_function
        self._match_comparison_error = 0

    """ PROPERTIES """
    """ DO_EXPORT"""
    # Getter
    @property
    def do_export(self):
        return self._do_export

    # Setter
    @do_export.setter
    def do_export(self, value):
        self._do_export = value

    # Deleter
    @do_export.deleter
    def do_export(self):
        del self._do_export

    """ OUTPUT_PATH """
    # Getter
    @property
    def output_path(self):
        return self._output_path

    # Setter
    @output_path.setter
    def output_path(self, value):
        self._output_path = value

    # Deleter
    @output_path.deleter
    def output_path(self):
        del self._output_path

    """ LOCAL_FILTER_ROW """
    # Getter
    @property
    def local_filter_row(self):
        return self._local_filter_row

    # Setter
    @local_filter_row.setter
    def local_filter_row(self, value):
        self._local_filter_row = value

    # Deleter
    @local_filter_row.deleter
    def local_filter_row(self):
        del self._local_filter_row

    """ OUTPUT_RENAME_DICT """
    # Getter
    @property
    def output_rename_dict(self):
        return self._output_rename_dict

    # Setter
    @output_rename_dict.setter
    def output_rename_dict(self, value):
        self._output_rename_dict = value

    # Deleter
    @output_rename_dict.deleter
    def output_rename_dict(self):
        del self._output_rename_dict

    """ OUTPUT_COLS_DICT """
    # Getter
    @property
    def output_cols_dict(self):
        return self._output_cols_dict

    # Setter
    @output_cols_dict.setter
    def output_cols_dict(self, value):
        self._output_cols_dict = value

    # Deleter
    @output_cols_dict.deleter
    def output_cols_dict(self):
        del self._output_cols_dict

    """ IMPORT_INCLUDE_COL """
    # Getter
    @property
    def import_include_col(self):
        return self._import_include_col

    # Setter
    @import_include_col.setter
    def import_include_col(self, value):
        self._import_include_col = value

    # Deleter
    @import_include_col.deleter
    def import_include_col(self):
        del self._import_include_col

    """ MATCH_COMPARISON_FUNCTION """
    # Getter
    @property
    def match_comparison_function(self):
        return self._match_comparison_function

    # Setter
    @match_comparison_function.setter
    def match_comparison_function(self, value):
        self._match_comparison_function = value

    # Deleter
    @match_comparison_function.deleter
    def match_comparison_function(self):
        del self._match_comparison_function

    """ MATCH_COMPARISON_ERROR """
    # Getter
    @property
    def match_comparison_error(self):
        return self._match_comparison_error

    # Setter
    @match_comparison_error.setter
    def match_comparison_error(self, value):
        self._match_comparison_error = value

    # Deleter
    @match_comparison_error.deleter
    def match_comparison_error(self):
        del self._match_comparison_error
