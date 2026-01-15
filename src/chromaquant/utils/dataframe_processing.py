#!/usr/bin/env python
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2025, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SUBPACKAGE FOR ADJUSTING AND TESTING DATAFRAMES

Julia Hancock
Started 11/12/2025

"""

""" FUNCTIONS """


def column_adjust(dataframe, add_col=[], remove_col=[], rename_dict={}):
    """
    Function used to add, remove, or rename
    columns in a passed DataFrame

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame to have columns adjusted.
    add_col : list, optional
        List of column headers to add, by default [].
    remove_col : list, optional
        List of column headers to remove, by default [].
    rename_dict : list, optional
        Dictionary of headers to rename as keys and
        new headers as values, by default {}.

    Returns
    -------
    pandas.DataFrame
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


def row_filter(dataframe, filter_dict):
    """
    Function used to filter a passed DataFrame
    such that it only contains certain values
    in specific columns
    ...

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame to have rows filtered.
    filter_dict : _type_
        Dictionary containing column names as keys and desired cell values
        as values

    Returns
    -------
    pandas.dataframe
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


def verify_column_not_empty(dataframe, column):
    """
    Function used to test whether a column in a passed
    DataFrame is empty

    ...

    Parameters
    ----------
    dataframe : pandas.DataFrame
        DataFrame containing column to be tested
    column : str
        Header of a column which may or may not contain values

    Returns
    -------
    bool
        Result of the conditional test: True if the column is
        not empty and False if the column is empty
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


def test_for_column_values(dataframe, column, test_values):
    """
    Function used to test for the presence or absence of
    passed values in some column of a given DataFrame

    ...
    Parameters
    ----------
    dataframe :
        _description_
    column : _type_
        _description_
    test_values : _type_
        _description_

    Returns
    -------
    _type_
        _description_
    """

    # Define a default test result dictionary
    test_result_dict = {test_value: False for test_value in test_values}

    # If the dataframe is not empty...
    if verify_column_not_empty(dataframe, column):

        # For each test value in the test_values list...
        for value in test_values:

            # If the column contains the test value at at least one row...
            if value in dataframe.loc[column].values.tolist():

                # Set the test_result_dict entry to True
                test_result_dict[value] = True

            # Otherwise, pass
            else:
                pass

    # Otherwise, pass
    else:
        pass

    return test_result_dict
