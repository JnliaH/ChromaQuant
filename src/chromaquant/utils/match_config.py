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

import pandas as pd
from collections.abc import Callable

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
    match_conditions = ConfigProperty()
    multiple_matches_rule = ConfigProperty()
    output_cols_dict = ConfigProperty()
    output_path = ConfigProperty()

    # Initialize
    def __init__(self,
                 do_export: bool = False,
                 import_include_col: list = None,
                 local_filter_row: dict = None,
                 match_conditions: list[dict[str, str | bool | float |
                                             Callable[[float | int | str,
                                                       pd.DataFrame,
                                                       float | int | str],
                                                      pd.DataFrame
                                                      ]]] = None,
                 multiple_matches_rule: Callable[[pd.DataFrame],
                                                 pd.Series] = None,
                 output_cols_dict: dict = None,
                 output_path: str = 'match_results.csv'):

        # Expected structure of match_conditions:
        # self.match_conditions = [{
        #                          'condition': self.IS_EQUAL,
        #                          NOTE: or another condition
        #                          'first_DF_column': {STRING},
        #                          'second_DF_column': {STRING},
        #                          'error': {FLOAT},
        #                          'or_equal': {BOOLEAN}
        #                          },
        #                         ...]

        # Define default match comparison function
        def default_comp_function(x):
            return x

        # Set descriptor values
        self.do_export = do_export
        self.import_include_col = import_include_col \
            if import_include_col is not None else []
        self.local_filter_row = local_filter_row \
            if local_filter_row is not None else {}
        self.match_conditions = match_conditions \
            if match_conditions is not None else []
        self.multiple_matches_rule = multiple_matches_rule \
            if multiple_matches_rule is not None else self.SELECT_FIRST_ROW
        self.output_cols_dict = output_cols_dict\
            if output_cols_dict is not None else {}
        self.output_path = output_path

    """ METHODS """

    # Method to add a new match condition
    def add_match_condition(self,
                            condition,
                            comparison,
                            error=0,
                            or_equal=False):

        # Check if comparison is a string
        try:
            comparison.split()
            # If can split comparison, assign both first and second
            # comparison to this one value
            first_comparison = comparison
            second_comparison = comparison
        # If comparison is not a string
        except Exception:
            # If the length is one...
            if len(comparison) == 1:
                # Set first and second comparison to this one value
                first_comparison = comparison[0]
                second_comparison = comparison[0]
            # If the length is two...
            if len(comparison) == 2:
                # Set the first and second comparison respectively
                first_comparison = comparison[0]
                second_comparison = comparison[1]
            # If the length is neither one or two, raise an error
            else:
                raise ValueError('Unexpected value passed for comparison.')

        # Append new match condition to list of conditions
        self.match_conditions.append(
            {
                'condition': condition,
                'first_DF_column': first_comparison,
                'second_DF_column': second_comparison,
                'error': error,
                'or_equal': or_equal
            }
        )

        return None

    """ STATIC METHODS """

    # Method to get a slice of a DataFrame where one of its
    # column's values are equal to some value
    @staticmethod
    def IS_EQUAL(value, DF, DF_column_name, error=0, or_equal=False):

        # Get a slice where the comparisons are exactly equal
        DF_slice = DF.loc[DF[DF_column_name] == value].copy()

        # Try to get a slice where the comparison is
        # within specified error margins
        try:

            # Define upper and lower limits
            series_value_max = value + error
            series_value_min = value - error

            # Get a slice
            DF_slice = \
                DF.loc[(DF[DF_column_name] >= series_value_min) &
                       (DF[DF_column_name] <= series_value_max)].copy()

        # If an error occurs when trying to get such a slice, pass
        # NOTE: This is intended to catch cases where comparison
        # values are non-numbers
        except Exception:
            pass

        return DF_slice

    # Method to get a slice of a DataFrame where one of its
    # column's values are less than some value
    # (i.e., a value is *greater than* the DataFrame value)
    @staticmethod
    def GREATER_THAN(value, DF, DF_column_name, error=0, or_equal=False):

        # Try to get a slice with condition
        try:

            # If the values can be equal...
            if or_equal:
                # Get a slice
                DF_slice = \
                    DF.loc[DF[DF_column_name] <= value].copy()

            # If the values cannot be equal...
            else:
                # Get a slice
                DF_slice = \
                    DF.loc[DF[DF_column_name] < value].copy()

        # If an error occurs when trying to get such a slice, pass
        # NOTE: This is intended to catch cases where comparison
        # values are non-numbers
        except Exception:

            # Get an empty DataFrame
            DF_slice = DF.loc[pd.Index([]), :].copy()

        return DF_slice

    # Method to get a slice of a DataFrame where one of its
    # column's values are greater than some value
    # (i.e., a value is *less than* the DataFrame value)
    @staticmethod
    def LESS_THAN(value, DF, DF_column_name, error=0, or_equal=False):

        # Try to get a slice with condition
        try:

            # If the values can be equal...
            if or_equal:
                # Get a slice
                DF_slice = \
                    DF.loc[DF[DF_column_name] >= value].copy()

            # If the values cannot be equal...
            else:
                # Get a slice
                DF_slice = \
                    DF.loc[DF[DF_column_name] > value].copy()

        # If an error occurs when trying to get such a slice, pass
        # NOTE: This is intended to catch cases where comparison
        # values are non-numbers
        except Exception:

            # Get an empty DataFrame
            DF_slice = DF.loc[pd.Index([]), :].copy()

        return DF_slice

    # Method that gets the first row of a slice, used as the default
    # method of selecting one row of a slice that meets match conditions
    @staticmethod
    def SELECT_FIRST_ROW(DF):

        # Get the first row of the DataFrame
        first_row = DF.loc[DF.index.min()]

        return first_row
