#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The Value class allows users to create objects to store one-dimensional
data (e.g., floats, integers, strings).

"""

import logging
from openpyxl.utils import get_column_letter
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from ..results import Results
from .dataset import DataSet
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Value class
class Value(DataSet):
    """
    Class used to store a single value alongside reporting information.

    Parameters
    ----------
    data : Any, optional
        Data to be stored.

    start_cell : str, optional
        Reference to cell in Excel where data will be reported. If data
        contains more than one item, refers to the top-left of report
        range. Must be a valid Excel cell (e.g., 'A1', '$B$2').

    sheet : str, optional
        Name of Excel worksheet (sheet within workbook) where data will
        be reported.

    header: str, optional
        Header to add above a dataset, equivalent to a title.

    results: Results, optional
        Results object that mediates this DataSet.

    Raises
    ------
    ValueError
        If sheet is set to a blank string.
    ValueError
        If start_cell is set to an invalid Excel cell.

    """

    def __init__(self,
                 data: Any = float('nan'),
                 start_cell: str = '',
                 sheet: str = '',
                 header: str = '',
                 results: Results = None):

        # Run DataSet initialization
        super().__init__(data=data,
                         start_cell=start_cell,
                         sheet=sheet,
                         type='Value',
                         header=header,
                         results=results)

        # Update the value
        self._update_value()

    """ PROPERTIES """
    # Define the reference property, ONLY DEFINE GETTER
    @property
    def reference(self):
        """
        Get the current reference object for the DataSet. Unable to set
        or delete this value as it is managed internally.
        """
        self._update_value()
        return self._reference

    # Redefining properties to include update_value
    # Data properties
    # Getter
    @property
    def data(self) -> Any:
        """
        Get, set, or delete data stored in the DataSet. Common types include
        str, bool, int, float, list, dict, or pandas DataFrame.
        """
        return self._data

    # Setter
    @data.setter
    def data(self, value: Any):
        self._data = value
        self._update_value()

    # Deleter
    @data.deleter
    def data(self):
        del self._data
        self._update_value()

    # Sheet properties
    # Getter
    @property
    def sheet(self) -> str:
        """
        Get, set, or delete the name of the Excel worksheet to report to.
        """
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value: str):
        if value == '':
            raise ValueError('Value sheet cannot be an empty string.')
        self._sheet = value
        self._update_value()
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet
        self._update_value()
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Start cell properties
    # Getter
    @property
    def start_cell(self) -> str:
        """
        Get, set, or delete the Excel reference where data will be reported.
        """
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value: str):
        try:
            # Get the cell's absolute indices
            self.start_column, self.start_row = self.get_cell_indices(value)
            # Set the starting cell
            self._start_cell = value
        except Exception as e:
            raise ValueError(f'Passed start cell is not valid: {e}')
        self._update_value()
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        del self.start_row, self.start_column
        self._update_value()
        if self._mediator is not None:
            self._mediator.update_datasets()

    """ METHODS """
    # Method to get the Value insert string
    @error_logging
    def insert(self) -> str:
        """
        Method that returns a unique identifier within a string insert. Used
        when composing dynamic formulas for reporting to Excel.

        Returns
        -------
        insert: str
            Formula insert containing unique Value identifier.

        """

        # Define insert
        insert = f'|key: {self.id}|'

        return insert

    # Method to update the value's reference
    @error_logging
    def _update_reference(self):
        """
        Method that updates the Value's reference dictionary.

        Returns
        -------
        None

        """

        # Get the column letter, adjusting from absolute
        column_letter = get_column_letter(self.start_column + 1)

        # Get a Boolean indicating whether the Table has a header
        has_header = False if self.header == '' else True

        # If there is a header...
        if has_header:

            # Get the Value name cell
            name_cell = \
                f"'{self._sheet}'!${column_letter}${self.start_row + 1}"

            # Get the Value data cell
            data_cell = \
                f"'{self._sheet}'!${column_letter}${self.start_row + 2}"

            # Update the reference object
            self._reference = \
                {'column_letter': column_letter,
                 'row': self.start_row + 1,
                 'sheet': self._sheet,
                 'name_cell': name_cell,
                 'data_cell': data_cell}

        # If there isn't a header...
        else:

            # Get the Value data cell
            data_cell = \
                f"'{self._sheet}'!${column_letter}${self.start_row + 1}"

            # Update the reference object
            self._reference = \
                {'column_letter': column_letter,
                 'row': self.start_row + 1,
                 'sheet': self._sheet,
                 'data_cell': data_cell}

        return None

    # Method to update the value
    @error_logging
    def _update_value(self):
        """
        Method that updates the current Value, mainly to update the reference.

        Returns
        -------
        None

        """

        # Initialize the reference object
        self._reference = {}

        # Try to update the reference
        # NOTE: will not work if there is no valid sheet or start_cell
        try:
            self._update_reference()
        except Exception:
            # logger.info(e)
            pass

        return None
