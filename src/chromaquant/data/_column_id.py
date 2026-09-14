#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The ColumnID class serves as an easy way to reference columns in Tables and
Breakdowns.

"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .table import Table
    from .breakdown import Breakdown
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the _ColumnID class
class _ColumnID:

    # Init method
    def __init__(self,
                 multicell_dataset: Table | Breakdown | None = None,
                 column_name: str | None = None):

        # Define basic attributes
        self._multicell_dataset = multicell_dataset
        self._column_name = column_name
        # Update the range
        self._update_reference()

    """ PROPERTIES """
    # Range
    # Getter
    @property
    def range(self):
        return self._range

    # Sheet
    # Getter
    @property
    def sheet(self):
        return self._sheet

    # Column name
    # Getter
    @property
    def column_name(self):
        return self._column_name

    # Setter
    @column_name.setter
    def column_name(self, value):
        self._column_name = value
        self._update_reference()

    # Multicell dataset
    # Getter
    @property
    def multicell_dataset(self):
        return self._multicell_dataset

    # Setter
    @multicell_dataset.setter
    def multicell_dataset(self, value):
        self._multicell_dataset = value
        self._update_reference()

    """ METHODS """
    def _update_reference(self):
        self._update_range()
        self._update_sheet()

    def _update_range(self):
        try:
            self._range = \
                self._multicell_dataset.reference[self._column_name]['range']
        except Exception:
            self._range = None

    def _update_sheet(self):
        try:
            self._sheet = \
                self._multicell_dataset.reference[self._column_name]['sheet']
        except Exception:
            self._sheet = None