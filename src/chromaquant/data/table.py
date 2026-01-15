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
from openpyxl.utils.cell import get_column_letter, \
                                column_index_from_string, \
                                coordinate_from_string
from .dataset import DataSet
from .match_tools import match_dataframes
from ..logging_and_handling import setup_logger, setup_error_logging
from ..utils import row_filter, column_adjust


""" LOGGING AND HANDLING """

# Get the logger
logger = setup_logger()

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Table class
class Table(DataSet):

    def __init__(self,
                 data_frame=pd.DataFrame(),
                 *args,
                 **kwargs):

        # Run DataSet initialization
        super().__init__(data_frame, *args, **kwargs)

        # Update the table
        self.update_table()

    """ PROPERTIES """
    # Define the references property
    @property
    def references(self):
        return self._references

    # Redefining properties to include update_table
    # Sheet properties
    # Getter
    @property
    def sheet(self):
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value):
        self._sheet = value
        self.update_table()

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet
        self.update_table()

    # Start cell properties
    # Getter
    @property
    def start_cell(self):
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value):
        self._start_cell = value
        self.update_table()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        self.update_table()

    """ METHODS """

    # Method to update column references
    @error_logging
    def update_references(self):

        # Get the indices for the start cell
        start_col_index, start_row_index = \
            self.get_cell_indices(self._start_cell)

        # For every column in columns...
        for column in self.columns:

            # Get the current column's letter
            col_letter = \
                self.get_column_letter_wrt_start_cell(column,
                                                      self._data,
                                                      start_col_index)

            # Update the references object
            self._references[column] = \
                {'column_letter': col_letter,
                 'start_row': start_row_index + 1,
                 'end_row': start_row_index + self.length,
                 'sheet': self._sheet,
                 'range': (f"'{self._sheet}'!"
                           f"${col_letter}${start_row_index + 1}:"
                           f"${col_letter}${start_row_index + self.length}")}

        return None

    # Method for updating otherwise static Table attributes
    @error_logging
    def update_table(self):

        # Update the length header
        self.length = \
            len(self._data)

        # Update the column header
        self.columns = \
            self._data.columns.tolist()

        # Initialize the references object
        self._references = {}

        # Try to update the references
        # NOTE: will not work if there is no valid sheet or start_cell
        try:
            self.update_references()
        except AttributeError as e:
            logger.info(e)
            pass

        return None

    # Method to add a new column to a table
    @error_logging
    def add_table_column(self,
                         column_name,
                         column_values=float('nan')):

        # Set every entry in the column to column_values
        # If column_values is an iterable, this will iterate
        # through it, otherwise it will set every entry to
        # the same value
        self._data[column_name] = column_values

        # Update the table
        self.update_table()

        return None

    # Match function
    def match(self, import_DF, local_comparison, import_comparison, **kwargs):
        """Matches imported to Table data by comparing one column from each.

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

        logger.debug('Table.match() called')

        """ EVALUATING ARGUMENTS """

        # Add the import dataframe to the local Signal's data object
        self.match_import_data = import_DF

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
        # If the current key is not permitted, raise an error
        self.check_dict_keys(kwargs, self.match_config)

        # Redefine match_config values using passed keyword arguments
        for key in kwargs:
            self.match_config[key] = kwargs[key]

        """ CREATE OR LOAD MATCH DATAFRAME """

        # Check if the match_data attribute exists,
        # warn that method will overwrite previous data
        if hasattr(self, 'match_data'):
            logger.warning('Overwriting previous match data.')
        # Otherwise, pass
        else:
            pass

        # Check if a match file already exists at the specified path
        try_open_tf, match_data = \
            self.try_open_file(pd.read_csv, self.match_config['output_path'])

        # If a match file already exists,
        # open it and save it to data object **SEE NOTE
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
        self.match_data = \
            self.match_import_data.copy()

        """ FILTER ROWS """
        # Adjust the dataframe according to match_config
        # Filter rows first in case desired filter includes a column
        # that will be renamed or removed
        self.match_data = row_filter(
                        self.match_data,
                        self.match_config['local_filter_row']
        )

        # Add column headers for columns to include from import
        self.match_data = column_adjust(
                        dataframe=self.match_data,
                        add_col=self.match_config['import_include_col']
        )

        """ MATCH DATAFRAMES """
        # Match the local and import data sets
        self.match_data = \
            match_dataframes(self.match_data,
                             self.match_import_data,
                             self.match_config)

        """ ADJUST OUTPUT """

        # Get the current columns in match_data
        match_cols = self.match_data.columns.tolist()

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
            self.match_data = column_adjust(
                            dataframe=self.match_data,
                            add_col=columns_to_add,
                            rename_dict=self.match_config['output_cols_dict']
            )
            # Finally, filter
            self.match_data = \
                self.match_data[output_cols_values]

        # Otherwise, pass
        else:
            pass

        """ (OPTIONAL) EXPORT TO FILE """

        # If the do_export value is True, export to output path
        if self.match_config['do_export']:
            self.export_to_csv(
                self.match_data,
                self.match_config['output_path']
            )
            logger.info('Match results exported to '
                        f'{self.match_config['output_path']}')

        # Otherwise, pass
        else:
            pass

        return None

    """ STATIC METHODS """
    # Function to return the row and column indices of a given cell
    @staticmethod
    def get_cell_indices(cell):

        # Split the cell string into individual coordinates
        col_letter, row_index = \
            coordinate_from_string(cell)

        # Get the starting column's index from its letter
        col_index = column_index_from_string(col_letter)

        return col_index, row_index

    # Function to get the letter coordinate of a column in a DataFrame
    # with respect to a starting column index
    @staticmethod
    def get_column_letter_wrt_start_cell(column, df, start_col_index):

        # Get the current column's letter
        col_letter = \
            get_column_letter(start_col_index +
                              df.columns.get_loc(column))

        return col_letter
