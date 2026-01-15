#!/usr/bin/env python
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2025, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

MATCH FUNCTION FOR DATAFRAME COMPARISONS

Julia Hancock
Started 1-15-2026

"""

import logging
from .match_tools import match_dataframes
from .file_tools import try_open_csv, export_to_csv
from .dataframe_processing import check_dict_keys, \
                                  column_adjust, \
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
def match(first_DF, second_DF, comparison, **kwargs):
    """Matches two DataFrames by comparing one column from each.

    Parameters
    ----------
    first_DF: pandas DataFrame
        A DataFrame containing data to be matched to data
        in second_DF, processed, then returned as match_data.
    second_DF: pandas DataFrame
        A DataFrame containing data to be matched to data in first_DF.

    Returns
    -------
    match_data : pandas DataFrame
        A DataFrame containing the results from matching.

    """

    """ EVALUATING ARGUMENTS """

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

    # Define default match comparison function
    def default_comp_function(x):
        return x

    # Define default match configuration values
    match_config = \
        {'do_export': False,
         'output_path': 'match_results.csv',
         'local_filter_row': {},
         'output_rename_dict': {},
         'output_cols_dict': {},
         'import_include_col': [],
         'match_comparison_function': default_comp_function,
         'match_comparison_error': 0}

    # Check that passed keyword arguments only include those expected
    # as listed in self.match_config
    # If the current key is not permitted, raise an error
    check_dict_keys(kwargs, match_config)

    # Redefine match_config values using passed keyword arguments
    for key in kwargs:
        match_config[key] = kwargs[key]

    # Add first and second comparison column names to match_config
    match_config['first_comparison'] = first_comparison
    match_config['second_comparison'] = second_comparison

    """ CREATE OR LOAD MATCH DATAFRAME """

    # Check if a match file already exists at the specified path
    try_open_tf, match_data = \
        try_open_csv(match_config['output_path'])

    # If a match file already exists,
    # open it and save it to data object **SEE NOTE
    if try_open_tf:
        # NOTE: Commented out potential feature to reopen previous match
        # file if one exists at the output path, untested
        # logger.info((f'Opening match file at '
        #            f'{self.match_config['output_path']}'))
        # self.data[match_key] = match_data
        logger.warning('Overwriting previous match data.')

    # Otherwise, pass
    else:
        # NOTE: See comment in if statement
        # Create a copy of the locally_defined dataframe
        # self.data[match_key] = \
        #    self.data[match_dict['local_data_key']].copy()
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
                    match_config['local_filter_row']
    )

    # Add column headers for columns to include from import
    match_data = column_adjust(
                    dataframe=match_data,
                    add_col=match_config['import_include_col']
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
    if match_config['output_cols_dict']:

        # Get the keys for output_cols_dict as list of original columns
        output_cols_keys = list(
            match_config['output_cols_dict'].keys()
        )
        # Get the values for output_cols_dict as list of new columns
        output_cols_values = list(
            match_config['output_cols_dict'].values()
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
                        rename_dict=match_config['output_cols_dict']
        )
        # Finally, filter
        match_data = \
            match_data[output_cols_values]

    # Otherwise, pass
    else:
        pass

    """ (OPTIONAL) EXPORT TO FILE """

    # If the do_export value is True, export to output path
    if match_config['do_export']:
        export_to_csv(
            match_data,
            match_config['output_path']
        )
        logger.info('Match results exported to '
                    f'{match_config['output_path']}')

    # Otherwise, pass
    else:
        pass

    return match_data
