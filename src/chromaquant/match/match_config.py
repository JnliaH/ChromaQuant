#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

CLASS DEFINITION FOR MATCH CONFIGURATION

This submodule contains the class definition for MatchConfig. Objects of
type MatchConfig are intended to contain user-specified parameters for
DataFrame matching (see match.py). Users can specify parameters such as
columns to include in a primary DataFrame from a second (import_include_col)
or where to output data (output_path). These objects can then be passed to
the match function from match.py or Table.match from a Table object.


"""

import pandas as pd
from typing import Any
from collections.abc import Callable

""" CLASS """


# Define ConfigProperty class
class ConfigProperty:

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
class MatchConfig:
    """
    Class used to define how data from two Pandas DataFrames should be matched.

    Parameters
    ----------
    do_export : bool, optional
        True if match results should be exported to .csv, by default False.
    import_include_col : list[str] | None, optional
        List of columns to include in second DataFrame in addition to
        columns from first DataFrame, by default None.
    local_filter_row : dict[str, str  |  bool  |  float  |  int] | None,
                        optional
        Dictonary containing name of column used to filter first dataframe
        as key and row value to filter by as value, by default None
    match_conditions : list[dict[str, Any]] | None, optional
        List of conditions by which to match the dataframes (See Notes),
        by default None
    multiple_hits_rule : Callable[[DataFrame, str], Series] | None,
                            optional
        Function that selects one Series (hit) from a DataFrame
        (multiple hits) with some built-in options like "SELECT_FIRST_ROW",
        by default None
    multiple_hits_column : str, optional
        Name of column by which to apply the multiple hits rule,
        by default ''
    output_cols_dict : dict[str, str] | None, optional
        Dictionary containing keys set to column names as written in
        matched datasets and values set to column names as desired in
        output DataFrame, by default None
    output_path : str, optional
        Path to output file including file name and extension,
        by default 'match_results.csv'

    Returns
    -------
    Any
        Value associated with each value attribute of the class from getter

    Raises
    ------
    ValueError
        If more than two strings are passed in a list for the comparison
        parameter when adding a match condition in add_match_condition.

    Notes
    -------
    Expected structure of match_conditions:

    [{
        'condition': cq.MatchConfig.IS_EQUAL,
        'first_DF_column': str,
        'second_DF_column': str,
        'error': float,
        'or_equal': bool
        },
    ...]

    The condition can be replaced with GREATER_THAN, LESS_THAN, or any
    user-defined function with the same arguments and return pattern.

    """

    # Create class instances of ConfigProperty for every property
    do_export = ConfigProperty()
    import_include_col = ConfigProperty()
    local_filter_row = ConfigProperty()
    match_conditions = ConfigProperty()
    multiple_hits_rule = ConfigProperty()
    multiple_hits_column = ConfigProperty()
    output_cols_dict = ConfigProperty()
    output_path = ConfigProperty()

    # Initialize
    def __init__(self,
                 do_export: bool = False,
                 import_include_col: list[str] | None = None,
                 local_filter_row:
                 dict[str, str | bool | float | int] | None = None,
                 match_conditions: list[dict[str, Any]] | None = None,
                 multiple_hits_rule:
                 Callable[[Any, pd.DataFrame, str, float | int, bool],
                          pd.Series] | None = None,
                 multiple_hits_column: str = '',
                 output_cols_dict: dict[str, str] | None = None,
                 output_path: str = 'match_results.csv'):

        # Define default match comparison function
        def default_comp_function(x):
            return x

        # Set descriptor values
        self.do_export: bool = do_export
        self.import_include_col: list[str] = import_include_col \
            if import_include_col is not None else []
        self.local_filter_row: dict[str, str | bool | float | int] = \
            local_filter_row if local_filter_row is not None else {}
        self.match_conditions: list[Any] = match_conditions \
            if match_conditions is not None else []
        self.multiple_hits_rule: Callable[[pd.DataFrame, str], pd.Series] = \
            multiple_hits_rule if multiple_hits_rule is not None \
            else self.SELECT_FIRST_ROW
        self.multiple_hits_column: str = multiple_hits_column
        self.output_cols_dict: dict = output_cols_dict\
            if output_cols_dict is not None else {}
        self.output_path: str = output_path

    """ METHODS """

    # Method to add a new match condition
    def add_match_condition(self,
                            condition: Callable[[pd.DataFrame, str],
                                                pd.Series],
                            comparison: str | list[str],
                            error: int | float = 0,
                            or_equal: bool = False):
        """
        Adds a new match condition to the MatchConfig instance.

        Parameters
        ----------
        condition : Callable(Any, pd.DataFrame, str, float | int, bool) -> pd.Series
            A condition that accepts a comparison value of any type, a
            DataFrame to compare the value against, the name of the column
            containing values to compare to the comparison value, and optional
            parameters for the error and whether to use inclusive inequalities
            (e.g., greater than or equal to), respectively.
        comparison : str or list[str]
            The name of the columns to compare across two DataFrames (if the
            name of the column is the same for both) or a list of two column
            names to compare (if the column names are different).
        error : float | int, optional
            A value by which one DataFrame's data can vary but still be matched
            to another DataFrame's data.
        or_equal : bool, optional
            True if inclusive inequalities can be used (e.g., >= or <=) and
            False if they cannot be used (e.g., > or <).

        Returns
        -------
        None

        """

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
    def IS_EQUAL(value: Any,
                 DF: pd.DataFrame,
                 DF_column_name: str,
                 error: float | int = 0,
                 or_equal: bool = False) -> pd.DataFrame:
        """
        Returns slice of a Dataframe where one of its column's
        values are equal to some value.

        Parameters
        ----------
        value : Any
            A value of any type, checked whether equal to any rows in DF.
        DF : Pandas DataFrame
            A Pandas DataFrame to compare against value.
        DF_column_name : str
            The name of the column in the DataFrame whose values
            are compared against value.
        error : float | int, optional
            A float or integer defining acceptable error for float or
            integer value, by default 0.
        or_equal : bool, optional
            True if value can be equal to values in DataFrame column
            (NOT USED BY THIS METHOD BUT KEPT FOR PARALLELISM WITH
            ALTERNATIVE MATCH CONDITIONS), by default False.

        Returns
        -------
        pd.DataFrame
            Slice of DataFrame where values in a given column are equal
            to a given value, optionally within a given error.

        """

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
    def GREATER_THAN(value: Any,
                     DF: pd.DataFrame,
                     DF_column_name: str,
                     error: float | int = 0,
                     or_equal: bool = False) -> pd.DataFrame:
        """
        Returns slice of a Dataframe where a passed value is greater
        than one of its column's values.

        Parameters
        ----------
        value : Any
            A value of any type, checked whether greater than any rows in DF.
        DF : Pandas DataFrame
            A Pandas DataFrame to compare against value.
        DF_column_name : str
            The name of the column in the DataFrame whose values
            are compared against value.
        error : float | int, optional
            A float or integer defining acceptable error for float or
            integer value (NOT USED BY THIS METHOD), by default 0.
        or_equal : bool, optional
            True if value can be equal to values in DataFrame column,
            by default False.

        Returns
        -------
        pd.DataFrame
            Slice of DataFrame where values in a given column are less than
            a given value.

        """

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
    def LESS_THAN(value: Any,
                  DF: pd.DataFrame,
                  DF_column_name: str,
                  error: float | int = 0,
                  or_equal: bool = False) -> pd.DataFrame:
        """
        Returns slice of a Dataframe where a passed value is less
        than one of its column's values.

        Parameters
        ----------
        value : Any
            A value of any type, checked whether less than any rows in DF.
        DF : Pandas DataFrame
            A Pandas DataFrame to compare against value.
        DF_column_name : str
            The name of the column in the DataFrame whose values
            are compared against value.
        error : float | int, optional
            A float or integer defining acceptable error for float or
            integer value (NOT USED BY THIS METHOD), by default 0.
        or_equal : bool, optional
            True if value can be equal to values in DataFrame column,
            by default False.

        Returns
        -------
        pd.DataFrame
            Slice of DataFrame where values in a given column are greater
            than a given value.

        """

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
    def SELECT_FIRST_ROW(DF: pd.DataFrame,
                         column_name: str) -> pd.Series:
        """Multiple hits rule to select first row of DataFrame.

        Parameters
        ----------
        DF : pd.DataFrame
            DataFrame to apply multiple hits rule to.
        column_name : str
            Name of column to consider in rule.

        Returns
        -------
        pd.Series
            A row from the passed DF.

        """

        # Get the first row of the DataFrame
        first_row = DF.loc[DF.index.min()]

        return first_row

    # Method that selects the row with the smallest value in a given column
    # NOTE: will return the first occurrence of the smallest value if multiple
    # values share the same minimum
    @staticmethod
    def SELECT_LOWEST_VALUE(DF: pd.DataFrame,
                            column_name: str) -> pd.Series:
        """Multiple hits rule to select row of DataFrame
        where column has lowest value

        Parameters
        ----------
        DF : pd.DataFrame
            DataFrame to apply multiple hits rule to.
        column_name : str
            Name of column to consider in rule.

        Returns
        -------
        pd.Series
            A row from the passed DF.

        """

        # Get the minimum value
        min_value_index = DF[column_name].idxmin()

        # Get the row with the smallest value
        min_value_row = DF.loc[min_value_index]

        return min_value_row

    # Method that selects the row with the largest value in a given column
    # NOTE: will return the first occurrence of the largest value if multiple
    # values share the same maximum
    @staticmethod
    def SELECT_HIGHEST_VALUE(DF: pd.DataFrame,
                             column_name: str) -> pd.Series:
        """Multiple hits rule to select row of DataFrame
        where column has highest value

        Parameters
        ----------
        DF : pd.DataFrame
            DataFrame to apply multiple hits rule to.
        column_name : str
            Name of column to consider in rule.

        Returns
        -------
        pd.Series
            A row from the passed DF.

        """

        # Get the maximum value
        max_value_index = DF[column_name].idxmax()

        # Get the row with the largest value
        max_value_row = DF.loc[max_value_index]

        return max_value_row
