#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

MATCH FUNCTION FOR DATAFRAME COMPARISONS

This submodule contains a function used in matching two Pandas DataFrames
based on a passed MatchConfig object (see match_config.py). It is used in
Table instances to match a DataFrame to the data contained in some Table.
This is useful for signal matching, response factor assignment, and other
related operations.

"""

import logging
from .match_config import MatchConfig
from .match_tools import match_dataframes
from ..utils.file_tools import try_open_csv, export_to_csv
from ..utils.dataframe_processing import column_adjust, \
                                         row_filter
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" FUNCTION """


# Match function
def match(first_DF,
          second_DF,
          match_config=MatchConfig()):
    """Matches data from two DataFrames

    Parameters
    ----------
    first_DF: pandas DataFrame
        A DataFrame containing data to be matched to data
        in second_DF, processed, then returned as match_data.
    second_DF: pandas DataFrame
        A DataFrame containing data to be matched to data in first_DF.
    match_config: MatchConfig
        A MatchConfig instance containing information on how to match
        the two data sets.

    Returns
    -------
    match_data : pandas DataFrame
        A DataFrame containing the results from matching.

    """

    """ EVALUATING ARGUMENTS """

    # If the match_config import_include_col list is empty...
    if not match_config.import_include_col:
        # Add all columns from the second dataframe
        match_config.import_include_col = \
            [column for column in second_DF.columns.tolist()
             if column not in first_DF.columns.tolist()]
    # Otherwise, pass
    else:
        pass

    """ CREATE OR LOAD MATCH DATAFRAME """

    # Check if a match file already exists at the specified path
    try_open_tf, match_data = \
        try_open_csv(match_config.output_path)

    # If a match file already exists,
    # open it and save it to data object **SEE NOTE
    if try_open_tf:
        # NOTE: Commented out potential feature to reopen previous match
        # file if one exists at the output path, untested
        # logger.info((f'Opening match file at '
        #            f'{self.match_config.output_path}'))
        # self.data[match_key] = match_data
        # logger.warning('Overwriting previous match data.')
        pass

    # Otherwise, pass
    else:
        # NOTE: See comment in if statement
        # Create a copy of the locally_defined dataframe
        # self.data[match_key] = \
        #    self.data[match_dict.local_data_key].copy()
        pass

    # Create a copy of the first DF
    match_data = \
        first_DF.copy()

    """ FILTER ROWS """
    # Adjust the dataframe according to match_config
    # Filter rows first in case desired filter includes a column
    # that will be renamed or removed
    match_data = row_filter(
                    match_data,
                    match_config.local_filter_row
    )

    # Add column headers for columns to include from import
    match_data = column_adjust(
                    dataframe=match_data,
                    add_col=match_config.import_include_col
    )

    """ MATCH DATAFRAMES """
    # Match the local and import data sets
    match_data = \
        match_dataframes(match_data,
                         second_DF,
                         match_config)

    """ ADJUST OUTPUT """

    # Get the current columns in match_data
    match_cols = match_data.columns.tolist()

    # If the output_cols_dict is not empty...
    if match_config.output_cols_dict:

        # Get the keys for output_cols_dict as list of original columns
        output_cols_keys = list(
            match_config.output_cols_dict.keys()
        )
        # Get the values for output_cols_dict as list of new columns
        output_cols_values = list(
            match_config.output_cols_dict.values()
        )

        # Filter the dataframe according to output_cols
        # NOTE: This preserves the column order as seen in output_cols_dict
        # First, add columns present in output_cols but not match_cols
        # And then rename columns using output_cols_dict
        columns_to_add = list(
            set(output_cols_keys).difference(set(match_cols))
        )
        match_data = column_adjust(
                        dataframe=match_data,
                        add_col=columns_to_add,
                        rename_dict=match_config.output_cols_dict
        )
        # Finally, filter
        match_data = \
            match_data[output_cols_values]

    # Otherwise, pass
    else:
        pass

    """ (OPTIONAL) EXPORT TO FILE """

    # If the do_export value is True, export to output path
    if match_config.do_export:
        export_to_csv(
            match_data,
            match_config.output_path
        )
        # logger.info('Match results exported to '
        #            f'{match_config.output_path}')

    # Otherwise, pass
    else:
        pass

    return match_data
