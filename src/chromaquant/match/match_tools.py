#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

TOOLS FOR MATCHING DATAFRAME ROWS ACCORDING TO A PASSED MODEL

..COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

Julia Hancock
Started 11-13-2025

"""

from pandas import DataFrame, Series
from typing import Any
from .match_config import MatchConfig

""" FUNCTIONS """


# Function that matches one DataFrame's values to another using some comparison
def match_dataframes(main_DF: DataFrame,
                     second_DF: DataFrame,
                     match_config: MatchConfig) -> DataFrame:
    """Matches data from two DataFrames by following a passed MatchConfig

    Parameters
    ----------
    main_DF : DataFrame
        A DataFrame with data to be matched,
        will serve as basis for returned results
    second_DF : DataFrame
        Another DataFrame with data to be matched
    match_config : MatchConfig
        A MatchConfig with parameters for matching, including information
        about columns to match by and columns to include in results

    Returns
    -------
    DataFrame
        A DataFrame containing data from main_DF plus some added data
        from second_DF as defined in match_config

    Raises
    ------
    ValueError
        If a DataFrame slice created from matching is of unexpected length,
        specifically a negative value.

    """

    # Function that adds data from one row to another
    def add_to_first(first: Series,
                     second: Series,
                     add_columns: list[str]):

        # Create a copy of the passed first_row
        new_first = first.copy()

        # For every column in add_columns...
        for column in add_columns:
            # Set the first row's entry to the second row's entry
            new_first.at[column] = second[column]

        return new_first

    # Function that finds all rows in a DataFrame that meet a condition
    # with respect to some different row
    def match_one_row_condition(row: Series,
                                DF: DataFrame,
                                match_condition: dict[str, Any]):

        # Create a copy of the passed main_row
        new_row = row.copy()

        # Get the comparison value from the new row
        row_value = new_row[match_condition['first_DF_column']]

        # Get a slice of DF that meets the condition
        DF_slice = \
            match_condition['condition'](row_value,
                                         DF,
                                         match_condition['second_DF_column'],
                                         error=match_condition['error'],
                                         or_equal=match_condition['or_equal'])

        # Try...
        try:
            # Add a column to the slice containing the error
            # between the actual and expected values
            DF_slice[f'{match_condition['second_DF_column']} Error'] = \
                [abs(DF_slice.at[i, match_condition['second_DF_column']])
                 - row_value for i, row_i in DF_slice.iterrows()]

        # If a TypeError occurs, add an empty column
        except TypeError:
            DF_slice[f'{match_condition['second_DF_column']} Error'] = \
                [0 for i, row_i in DF_slice.iterrows()]

        return DF_slice

    # Create a copy of the passed DataFrames
    new_main_DF = main_DF.copy()
    new_second_DF = second_DF.copy()

    # For every row in the main dataframe...
    for i, row in main_DF.iterrows():

        # Get a copy of the second DataFrame
        second_DF_slice = new_second_DF.copy()

        # Initialize an index for number of conditions applied
        j = 0

        # For every condition passed...
        for condition in match_config.match_conditions:

            # Get a slice of the second DataFrame that meets the condition
            second_DF_slice = match_one_row_condition(row,
                                                      second_DF_slice,
                                                      condition)

            # Increment j
            j += 1

        # If the slice is longer than one row...
        if len(second_DF_slice) > 1:

            # Get the name of the column used in selecting one hit of multiple
            column_name = match_config.multiple_hits_column

            # Add the values of some row in the slice to the current row
            # NOTE: uses the match_config's rule
            # on handling multiple row matches
            new_main_row = \
                add_to_first(row,
                             match_config.multiple_hits_rule(
                                 second_DF_slice,
                                 column_name),
                             match_config.import_include_col)

        # Otherwise, if the slice is just one row...
        elif len(second_DF_slice) == 1:

            # Add the values of the first row in the slice to the current row
            new_main_row = \
                add_to_first(row,
                             second_DF_slice.loc[
                              second_DF_slice.index.min()],
                             match_config.import_include_col)

        # Otherwise, if the slice is of length zero...
        elif len(second_DF_slice) == 0:

            # Create a copy of the current row
            new_main_row = row.copy()

            # For every column to be added from the second DataFrame...
            for column in match_config.import_include_col:
                # Add a None entry to that column in the new row
                new_main_row.at[column] = None

        # Otherwise, raise an error
        else:
            raise ValueError('Second slice of unexpected length.')

        # Add the new row to the current index in the main DataFrame
        new_main_DF.loc[i] = new_main_row

    return new_main_DF
