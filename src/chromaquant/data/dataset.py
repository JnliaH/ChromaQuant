#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The DataSet class serves as the parent class for the Value, Table,
and Breakdown classes. It contains simple property definitions for
the starting cell, worksheet, data, and header. It also defines the
behavior of DataSets as mediated objects when assigned a mediator
like a Results instance.

"""

import logging
from openpyxl.utils.cell import coordinate_from_string, \
                                column_index_from_string
from typing import Any, TYPE_CHECKING
if TYPE_CHECKING:
    from ..results import Results
import uuid
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the DataSet class
class DataSet:
    """
    Class used to store data alongside reporting information.

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

    type: str, optional
        Type of DataSet, used by child classes to identify their type.

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

    Notes
    -------
    This class is primarily internal, and its child classes (e.g., Table)
    are the primary API for users to interact with.

    """

    # Initialize
    def __init__(self,
                 data: Any = float('nan'),
                 start_cell: str = '',
                 sheet: str = '',
                 type: str = 'DataSet',
                 header: str = '',
                 results: Results = None):

        # Initialize instance attributes
        self.type = type
        self._start_cell = start_cell if start_cell != '' else '$A$1'
        self._sheet = sheet if sheet != '' else 'Sheet1'
        self._header = header
        self._reference: dict[str, Any] = {}
        self.start_column, self.start_row = \
            self.get_cell_indices(self._start_cell)

        # Initialize data attribute
        self._data = data

        # Create unique ID for the instance
        self.id = str(uuid.uuid4())

        # Add a mediator attribute
        self._mediator = results

    # Define the object representation by including its data
    def __repr__(self):
        return f"Contents of chromaquant.{self.type} Object:\n{self._data}"

    """ PROPERTIES """
    # Define the reference property, ONLY DEFINE GETTER
    @property
    def reference(self) -> dict[str, Any]:
        """
        Get the current reference object for the DataSet. Unable to set
        or delete this value as it is managed internally.
        """
        return self._reference

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
    def data(self, value: Any) -> None:
        self._data = value

    # Deleter
    @data.deleter
    def data(self) -> None:
        del self._data

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
            raise ValueError('Worksheet cannot be an empty string.')
        self._sheet = value
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet

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
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell
        del self.start_row, self.start_column

    # Header properties
    # Getter
    @property
    def header(self) -> str:
        """
        Get, set, or delete the header to add above a dataset.
        """
        return self._header

    # Setter
    @header.setter
    def header(self, value: str):
        self._header = value
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Deleter
    @header.deleter
    def header(self):
        del self._header
        if self._mediator is not None:
            self._mediator.update_datasets()

    # Mediator properties
    # Getter
    @property
    def mediator(self) -> str:
        """
        Get or set the mediator object that controls the interactions
        between this DataSet and colleague objects.
        """
        return self._mediator

    # Setter
    @mediator.setter
    def mediator(self, mediator: Results):
        self._mediator = mediator

    """ STATIC METHODS """

    # Static method to get the absolute indices of a cell
    @staticmethod
    def get_cell_indices(cell: str) -> tuple[int, int]:
        """
        Static method that returns the absolute indices of a cell.

        Parameters
        ----------
        cell : str
            Cell reference (e.g., 'A1', '$B$2').

        Returns
        -------
        column_index: int
            Absolute index of the reference column (e.g., 2 for 'C1').
        row_index: int
            Absolute index of the reference row (e.g., 0 for 'C1').

        """

        # Split the coordinate
        column_index, row_index = \
            coordinate_from_string(cell)

        # Get the absolute row by subtracting one
        row_index = row_index - 1

        # Get the column index from the string, adjusting to get absolute
        column_index = \
            column_index_from_string(column_index) - 1

        return column_index, row_index
