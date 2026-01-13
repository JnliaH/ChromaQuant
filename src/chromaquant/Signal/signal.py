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

CLASS DEFINITIONS FOR SIGNAL

Julia Hancock
Started 11-11-2025

"""

import os
import pandas as pd
from chromaquant import import_local_packages as ilp
from chromaquant import logging_and_handling as lah
from .match_tools import match_dataframes

""" LOGGING AND HANDLING """

# Get the logger
logger = lah.setup_logger()

# Get an error logging decorator
error_logging = lah.setup_error_logging(logger)

""" LOCAL PACKAGES """

# Get absolute directories for subpackages
subpack_dir = ilp.get_local_package_directories()

# Import all local packages
hd = ilp.import_from_path("hd", subpack_dir['Handle'])

""" CLASSES """


# Define the Signal class
class Signal:

    # Initialize class
    def __init__(self, signal_name, **kwargs):
        """__init__ _summary_

        Parameters
        ----------
        signal_name : str
            Name assigned to signal.

        """

        # Extract the name
        self.signal_name = signal_name

        # Initialize a data object that will contain imported data
        self.data = {}

        # Extract passed keywork arguments
        self.create_attributes_kwargs('signalkwarg', kwargs)

    """ METHODS """
    # Import data
    def data_import(self, directory, data_key):
        """data_import _summary_

        Parameters
        ----------
        directory : str
            Full path to the data file of interest, including file name.
        data_key : str
            Name to assign imported data when using the "data" object.

        Returns
        -------
        None

        """

        # Read data from the provided directory
        self.data[data_key] = pd.read_csv(directory, index_col=False)

        return None

    # Function to create instance attributes for each passed keyword argument
    def create_attributes_kwargs(self, prefix, kwargs):

        # For every key-value pair in kwargs...
        for key, value in kwargs.items():
            # Create an attribute name using the passed prefix
            attribute_name = prefix + '_' + key
            # Set attribute using name and key-value pair
            setattr(self, attribute_name, value)

        return None

    # Match function
    def match(self, import_DF, match_dict, **kwargs):
        """match _summary_

        This function matches a quantitative data set of a QuantSignal
        instance with a qualitative data set from some other Signal
        instance or child instance by comparing one column of values
        from one instance with another column from another instance

        Parameters
        ----------
        import_DF: pandas DataFrame
            A DataFrame containing data to be matched to data
            in the local Signal

        match_dict : dict
            A dictionary specifying the data keys and comparison column
            headers for the local and import DataFrames

        Returns
        -------
        None

        """

        logger.debug('QuantSignal.match() called')

        """ EVALUATING ARGUMENTS """

        # List of keys required in the passed dictionary
        required_keys = ('local_data_key',
                         'local_comparison',
                         'import_comparison',
                         'match_data_key')

        # Check that the passed match_dict and contains all keys
        self.check_keys(match_dict, required_keys)

        # Extract the passed match dictionary
        self.match_dict = match_dict

        # Get the match_data_key separately for convenience
        match_key = match_dict['match_data_key']

        # Add the import dataframe to the local Signal's data object
        self.data['match_import_data'] = import_DF

        # Define default match comparison function
        def default_comp_function(x):
            return x

        # Define default match configuration values
        self.match_config = \
            {'do_export': False,
             'output_path': 'match_results',
             'local_filter_row': {},
             'output_rename_dict': {},
             'output_cols_dict': {},
             'import_include_col': [],
             'match_comparison_function': default_comp_function,
             'match_comparison_error': 0}

        # Check that passed keyword arguments only include those expected
        # as listed in self.match_config
        self.check_kwargs(kwargs, self.match_config)

        # Redefine match_config values using passed keyword arguments
        for key in kwargs:
            self.match_config[key] = kwargs[key]

        # logger.debug((f'QuantSignal.match_config values set to '
        #              f'{self.match_config}'))

        """ CREATE OR LOAD MATCH DATAFRAME """

        # Check if the match_data key is already in use
        if match_key in self.data:
            logger.warning('Overwriting previous match'
                           f' data at key {match_key}')

        else:
            pass

        # Check if a match file already exists at the specified path
        try_open_tf, match_data = \
            self.try_open_file(pd.read_csv, self.match_config['output_path'])

        # If a match file already exists, open it and save it to data object
        if try_open_tf:
            # NOTE: Commented out potential feature to reopen previous match
            # file if one exists at the output path, untested
            # logger.info((f'Opening match file at '
            #            f'{self.match_config['output_path']}'))
            # self.data[match_key] = match_data
            logger.warning('Overwriting file at '
                           f'{self.match_config['output_path']}')

        # Otherwise, pass
        else:
            # NOTE: See comment in if statement
            # Create a copy of the locally_defined dataframe
            # self.data[match_key] = \
            #    self.data[match_dict['local_data_key']].copy()
            pass

        # Create a copy of the locally_defined dataframe
        self.data[match_key] = \
            self.data[match_dict['local_data_key']].copy()

        """ FILTER ROWS """
        # Adjust the dataframe according to match_config
        # Filter rows first in case desired filter includes a column
        # that will be renamed or removed
        self.data[match_key] = hd.row_filter(
                                    self.data[match_key],
                                    self.match_config['local_filter_row']
        )

        # Add column headers for columns to include from import
        self.data[match_key] = hd.column_adjust(
                        dataframe=self.data[match_key],
                        add_col=self.match_config['import_include_col']
        )

        # Debug statement to see contents of match_data prior to matching
        # logger.debug((f"self.data['{match_key}'] set to \n"
        #             f"{self.data[match_key]}"))
        # logger.debug((f"self.data['match_import_data'] set to \n"
        #              f"{self.data['match_import_data']}"))

        """ MATCH DATAFRAMES """
        # Match the local and import data sets
        self.data[match_key] = \
            match_dataframes(self.data[match_key],
                             self.data['match_import_data'],
                             self.match_dict,
                             self.match_config)

        """ ADJUST OUTPUT """

        # Get the current columns in match_data
        match_cols = self.data[match_key].columns.tolist()

        # If the output_cols_dict is not empty...
        if self.match_config['output_cols_dict']:

            # Get the keys for output_cols_dict as list of original columns
            output_cols_keys = list(
                self.match_config['output_cols_dict'].keys()
            )
            # Get the values for output_cols_dict as list of new columns
            output_cols_values = list(
                self.match_config['output_cols_dict'].values()
            )

            # Filter the dataframe according to output_cols
            # NOTE: This preserves the column order as seen in output_cols_dict
            # First, add columns present in output_cols but not match_cols
            # And then rename columns using output_cols_dict
            columns_to_add = list(
                set(output_cols_keys).difference(set(match_cols))
            )
            self.data[match_key] = hd.column_adjust(
                            dataframe=self.data[match_key],
                            add_col=columns_to_add,
                            rename_dict=self.match_config['output_cols_dict']
            )
            # Finally, filter
            self.data[match_key] = \
                self.data[match_key][output_cols_values]

        # Otherwise, pass
        else:
            pass

        # Debug statement post-matching
        # logger.debug((f"self.data['{match_key}'] set to \n"
        #             f"{self.data[match_key]}"))

        """ (OPTIONAL) EXPORT TO FILE """

        # If the do_export value is True, export to output path
        if self.match_config['do_export']:
            self.export_to_csv(
                self.data[match_key],
                self.match_config['output_path']
            )
            logger.info('Match results exported to '
                        f'{self.match_config['output_path']}')

        # Otherwise, pass
        else:
            pass

        return None

    """ STATIC METHODS """

    # Static method to export data to a .csv file
    @staticmethod
    def export_to_csv(dataframe, parent, name=''):
        """export_to_csv _summary_

        Parameters
        ----------
        dataframe : dataframe
            Passed Pandas dataframe.
        parent : string
            Name of parent directory for exported file.
        name : string
            Name of file to be exported.

        Returns
        -------
        None
        """

        # If the name argument is passed...
        if name:
            # Construct a full path from the passed
            # parent directory and file name
            full_path = os.path.join(parent, name, '.csv')
        # Otherwise...
        else:
            # Set the full path to the parent
            full_path = parent

        # Export the dataframe to the full path
        dataframe.to_csv(full_path, index=False)

        return None

    # Static method to try to open a file using a passed function
    @staticmethod
    def try_open_file(func, path, *args, **kwargs):

        # Predefine the conditional Boolean result
        tf = False

        # Try opening the file, if it works then set tf to True
        try:
            data = func(path, *args, **kwargs)
            tf = True

        # If cannot open file, log and set tf to False
        except Exception as e:
            logger.info(f'Could not open {path}, got {e}')
            data = []
            tf = False

        return tf, data

    # Static method to check if a dataframe contains required columns
    @staticmethod
    def check_dataframe_columns(dataframe, column_list):

        return None

    """ STATIC ERROR METHODS """
    # Static method to check that all keys exist in the passed dictionary
    @staticmethod
    def check_keys(dict, necessary_keys):
        """check_keys _summary_

        Parameters
        ----------
        dict : dict
            Dictionary to be tested.
        necessary_keys : list
            List of keys as strings to be checked against passed dictionary.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If key is not present in the dictionary, raise an error.
        """

        # For every key in the passed list...
        for key in necessary_keys:
            # If the key is absent from the dictionary...
            if key not in dict:
                # Raise an error
                raise ValueError(f"Missing required key: '{key}'")
            # Otherwise, pass
            else:
                pass

        return None

    # Static method to check that the keys passed in a **kwargs argument
    # match the expected keys as listed in a dictionary
    @staticmethod
    def check_kwargs(user_kwargs, expected_dict):
        """check_kwargs _summary_

        Parameters
        ----------
        user_kwargs : dict
            Dictionary from kwargs to iterate through.
        expected_dict : dict
            Dictionary outlining expected keys.

        Returns
        -------
        None

        Raises
        ------
        TypeError
            Error raised if user passed unexpected key
        """

        # For every key-value pair in the user_kwargs dictionary...
        for user_key in user_kwargs:

            # If the key is not expected, raise TypeError
            if user_key not in expected_dict:
                raise TypeError(f"Passed key '{user_key}' not expected")

            # Otherwise, pass
            else:
                pass

        return None
