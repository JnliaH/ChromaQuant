#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This submodule contains the class definition for MatchConfig. Objects of
type MatchConfig are intended to contain user-specified parameters for
DataFrame matching (see match.py). Users can specify parameters such as
columns to include in a primary DataFrame from a second (import_include_col)
or where to output data (output_path). These objects can then be passed to
the match function from match.py or Table.match from a Table object.


"""

import logging
import pandas as pd
from typing import Any
from collections.abc import Callable
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

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

    Raises
    ------
    ValueError
        If more than two strings are passed in a list for the comparison
        parameter when adding a match condition in add_match_condition.

    Notes
    -------
    The expected structure of match_conditions is as follows::

        [{
            'condition': cq.MatchConfig.IS_EQUAL,
            'first_DF_column': str,
            'second_DF_column': str,
            'kwargs': {
                'error': float (optional),
                'or_equal': bool (optional),
                'value_function': Callable (optional)
                }
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
                            kwargs: dict[str, Any] = {}):
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

        kwargs : dict[str, Any]
            A dictionary of additional keyword arguments to pass to the match
            condition. See each match condition option for applicable keywords.

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

        # Create new match condition dictionary
        match_condition = {
                'condition': condition,
                'first_DF_column': first_comparison,
                'second_DF_column': second_comparison,
                'kwargs': kwargs
            }

        # Append new match condition to list of conditions
        self.match_conditions.append(match_condition)

        return None

    """ STATIC METHODS """

    """ CONDITIONS """
    # Method to get a slice of a DataFrame where one of its
    # column's values are equal to some value
    @staticmethod
    def IS_EQUAL(value: Any,
                 DF: pd.DataFrame,
                 DF_column_name: str,
                 error: float | int = 0) -> pd.DataFrame:
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

            # Add a column to the slice containing the error
            # between the actual and expected values
            DF_slice[f'{DF_column_name} Error'] = \
                [abs(DF_slice.at[i, DF_column_name]
                 - value) for i, row_i in DF_slice.iterrows()]

        # If an error occurs when trying to get such a slice, pass
        # NOTE: This is intended to catch cases where comparison
        # values are non-numbers
        # Also, add an empty error column
        except TypeError:
            DF_slice['Value Function Error'] = \
                [0 for i, row_i in DF_slice.iterrows()]

        return DF_slice

    # Method to get a slice of a DataFrame where one of its
    # column's values are less than some value
    # (i.e., a value is *greater than* the DataFrame value)
    @staticmethod
    def GREATER_THAN(value: Any,
                     DF: pd.DataFrame,
                     DF_column_name: str,
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

    # Method to get a slice of a DataFrame where one of its
    # column's values passed through a function are equal to some value
    # (i.e., column_value = f(some_value))
    @staticmethod
    def FUNCTION_OF(value: Any,
                    DF: pd.DataFrame,
                    DF_column_name: str,
                    value_function: Callable[[Any], Any],
                    error: float | int = 0) -> pd.DataFrame:
        """
        Returns slice of a DataFrame where a passed value is a function
        of one of its column's values.

        Parameters
        ----------
        value : Any
            A value of any type, checked if a function of a DataFrame's
            values.

        DF : Pandas DataFrame
            A Pandas DataFrame to compare against value.

        DF_column_name : str
            The name of the column in the DataFrame whose values
            are compared against value.

        value_function : Callable[[Any], Any]
            A function that accepts a DataFrame's value and returns a value
            that should be equal to some passed value.

        error : float | int, optional
            A float or integer defining acceptable error for float or
            integer value, by default 0.

        Returns
        -------
        pd.DataFrame
            Slice of DataFrame where some value in a given column passed
            through a function is equal to a passed value.

        """

        # Get a copy of the passed DataFrame
        DF_copy = DF.copy()

        # Add a column to the DataFrame where each value is a function
        # of the corresponding row under DF_column_name
        DF_copy['value_function'] = \
            DF_copy[DF_column_name].apply(value_function)

        # Get a slice where the comparisons are exactly equal
        DF_slice = DF.loc[DF['value_function'] == value].copy()

        # Try to get a slice where the comparison is
        # within specified error margins
        try:

            # Define upper and lower limits
            series_value_max = value + error
            series_value_min = value - error

            # Get a slice
            DF_slice = \
                DF.loc[(DF['value_function'] >= series_value_min) &
                       (DF['value_function'] <= series_value_max)].copy()

            # Add a column to the slice containing the error
            # between the actual and expected values
            DF_slice['Value Function Error'] = \
                [abs(DF_slice.at[i, 'value_function']
                 - value) for i, row_i in DF_slice.iterrows()]

        # If an error occurs when trying to get such a slice, pass
        # NOTE: This is intended to catch cases where comparison
        # values are non-numbers
        # Also, add an empty error column
        except TypeError:
            DF_slice['Value Function Error'] = \
                [0 for i, row_i in DF_slice.iterrows()]

        return DF_slice

    """ MULTIPLE HITS RULES """
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
    # NOTE: will default to selecting the first row if DF contains all nan
    # under column_name
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

        # Try...
        try:
            # To get the minimum value
            min_value_index = DF[column_name].idxmin()

            # Get the row with the smallest value
            min_value_row = DF.loc[min_value_index]

        # If a KeyError is raised...
        except KeyError:

            # Log a warning
            logger.warning(
                'Highest value could not be selected due to a '
                'KeyError, likely because all top matches had NaN '
                'under the multiple hits column'
                )

            # Get the first row of the DataFrame
            min_value_row = DF.loc[DF.index.min()]

        return min_value_row

    # Method that selects the row with the largest value in a given column
    # NOTE: will return the first occurrence of the largest value if multiple
    # values share the same maximum
    # NOTE: will default to selecting the first row if DF contains all nan
    # under column_name
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

        # Try...
        try:
            # To get the maximum value
            max_value_index = DF[column_name].idxmax()

            # Get the row with the largest value
            max_value_row = DF.loc[max_value_index]

        # If a KeyError is raised...
        except KeyError:

            # Log a warning
            logger.warning(
                'Highest value could not be selected due to a '
                'KeyError, likely because all top matches had NaN '
                'under the multiple hits column'
                )

            # Get the first row of the DataFrame
            max_value_row = DF.loc[DF.index.min()]

        return max_value_row
