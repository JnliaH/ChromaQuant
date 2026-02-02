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

CLASS DEFINITION FOR DATASETS

Julia Hancock
Started 01-12-2025

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
        return self._reference

    # Data properties
    # Getter
    @property
    def data(self) -> Any:
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
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value: str):
        self._sheet = value

    # Deleter
    @sheet.deleter
    def sheet(self):
        del self._sheet

    # Start cell properties
    # Getter
    @property
    def start_cell(self) -> str:
        return self._start_cell

    # Setter
    @start_cell.setter
    def start_cell(self, value: str):
        self._start_cell = value

    # Deleter
    @start_cell.deleter
    def start_cell(self):
        del self._start_cell

    # Header properties
    # Getter
    @property
    def header(self) -> str:
        return self._header

    # Setter
    @header.setter
    def header(self, value: str):
        self._header = value

    # Deleter
    @header.deleter
    def header(self):
        del self._header

    # Mediator properties
    # Getter
    @property
    def mediator(self) -> str:
        return self._mediator

    # Setter
    @mediator.setter
    def mediator(self, mediator: Results):
        self._mediator = mediator

    """ STATIC METHODS """

    # Static method to get the absolute indices of a cell
    @staticmethod
    def get_cell_indices(cell: str) -> tuple[int, int]:

        # Split the coordinate
        column_index, row_index = \
            coordinate_from_string(cell)

        # Get the absolute row by subtracting one
        row_index = row_index - 1

        # Get the column index from the string, adjusting to get absolute
        column_index = \
            column_index_from_string(column_index) - 1

        return column_index, row_index
