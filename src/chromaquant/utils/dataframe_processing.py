#!/usr/bin/env python
"""

The DataFrame Processing submodule contains a number of functions used
internally (e.g., by the Match module) to perform certain operations on
Pandas DataFrames like adding new columns or filtering rows by some value.

"""

from typing import Any
from pandas import DataFrame, Series

""" FUNCTIONS """


# Function to loop through keys in a passed dictionary and
# check them against a list of permitted keys or dictionary
# with permitted keys
def check_dict_keys(dictionary: dict[Any, Any], permitted: list[Any]):
    """
    Function that checks all keys in a passed dictionary against a list
    of permissible keys.

    Parameters
    ----------
    dictionary : dict[Any, Any]
        The dictionary containing keys to be checked against permitted.
    permitted : list[Any]
        A list of permitted keys.

    Returns
    -------
    None.

    Raises
    ------
    ValueError
        If at least one key in the dictionary is not in the list of
        permitted keys.

    """

    # For every key-value pair in the dictionary...
    for key, value in dictionary.items():

        # If the current key is not permitted, raise an error
        if key not in permitted:
            raise ValueError(f'{key} is not a valid argument')

        # Otherwise, pass
        else:
            pass

    return None


# Function to add, remove, or rename columns in a DataFrame
def column_adjust(dataframe: DataFrame,
                  add_col: list[str] = [],
                  remove_col: list[str] = [],
                  rename_dict: dict[str, str] = {}) -> DataFrame:
    """
    Function used to add, remove, or rename
    columns in a passed DataFrame

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame to have columns adjusted.
    add_col : list[str], optional
        List of column headers to add, by default [].
    remove_col : list[str], optional
        List of column headers to remove, by default [].
    rename_dict : dict, optional
        Dictionary of headers to rename as keys and
        new headers as values, by default {}.

    Returns
    -------
    new_dataframe : pandas.DataFrame
        DataFrame post-adjustments.
    """

    # Define a new dataframe
    new_dataframe = dataframe.copy()

    # For each column in add_col...
    if add_col:
        for column in add_col:
            # Create a new column and assign all values to NaN
            # NOTE: if the column already exists, this will
            # clear existing data
            new_dataframe[column] = None

    # Rename columns using key-value pairs in rename_dict
    if rename_dict:
        new_dataframe = new_dataframe.rename(columns=rename_dict)

    # Remove dataframe columns as specified in remove_col...
    if remove_col:
        new_dataframe = dataframe.drop(remove_col, axis=1)

    return new_dataframe


# Function to filter a DataFrame based on certain values in rows
def row_filter(dataframe: DataFrame, filter_dict: dict) -> DataFrame:
    """
    Function used to filter a passed DataFrame
    such that it only contains certain values
    in specific columns.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame to have rows filtered.
    filter_dict : dict
        Dictionary containing column names as keys and desired cell values
        as values.

    Returns
    -------
    new_dataframe : pandas.dataframe
        Dataframe post-filtering.

    """

    # Define a new dataframe
    new_dataframe = dataframe.copy()

    # Filter the new dataframe to only include rows where the value
    # in some column is equal to the value associated with the key
    # in filter_dict that matches that column's header
    for key, value in filter_dict.items():
        new_dataframe = new_dataframe.loc[new_dataframe[key] == value]

    return new_dataframe


# Function to check whether a column is empty
def verify_column_not_empty(dataframe: DataFrame, column: str) -> bool:
    """
    Function used to test whether a column in a passed
    DataFrame is empty.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame containing column to be tested.
    column : str
        Header of a column which may or may not contain values.

    Returns
    -------
    test_result : bool
        Result of the conditional test: True if the column is
        not empty and False if the column is empty.

    """

    # Define a default test result
    test_result = False

    # If there is any value in the passed column...
    if dataframe[column].any():

        # Redefine test result to True
        test_result = True

    # Otherwise, set to False
    else:
        test_result = False

    return test_result


# Function to test whether certain values exist in a column
def test_for_column_values(dataframe: DataFrame,
                           column_name: str,
                           test_values: list[Any]) -> dict[Any, bool]:
    """
    Function used to test for the presence or absence of
    passed values in some column of a given DataFrame.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        A DataFrame containing a column with a name matching column_name.

    column : str
        The name of a column of interest.

    test_values : list[Any]
        A list of values to be searched for in the column of interest.

    Returns
    -------
    test_result_dict: dict[Any, bool]
        A dictionary containing passed test_values as keys and bools
        indicating the presence or absence of each test value in the
        column of interest.

    """

    # Define a default test result dictionary
    test_result_dict = {test_value: False for test_value in test_values}

    # If the dataframe is not empty...
    if verify_column_not_empty(dataframe, column_name):

        # For each test value in the test_values list...
        for value in test_values:

            # If the column contains the test value at at least one row...
            if value in dataframe.loc[column_name].values.tolist():

                # Set the test_result_dict entry to True
                test_result_dict[value] = True

            # Otherwise, pass
            else:
                pass

    # Otherwise, pass
    else:
        pass

    return test_result_dict


# Function that adds data from one row to another
def add_columns_from_one_row_to_another(first_row: Series,
                                        second_row: Series,
                                        add_columns: list[str]) -> Series:
    """
    Function that adds data from one row to another using a list of column
    names.

    Parameters
    ----------
    first_row : pandas.Series
        A row (or Series) to have data appended to it.
    second_row : pandas.Series
        A row (or Series) containing data to be added to another row (or
        Series).
    add_columns : list[str]
        A list of column names indicating which data from second_row to add
        to first_row.

    Returns
    -------
    new_first : pandas.Series
        A copy of first_row containing added data.

    """

    # Create a copy of the passed first_row
    new_first = first_row.copy()

    # For every column in add_columns...
    for column in add_columns:
        # Set the first row's entry to the second row's entry
        new_first.at[column] = second_row[column]

    return new_first
