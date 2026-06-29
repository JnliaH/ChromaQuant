#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The ColumnID class serves as an easy way to reference columns in Tables and
Breakdowns.

"""

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

    """ PROPERTIES """
    # Multicell dataset
    # Getter
    @property
    def multicell_dataset(self):
        return self._multicell_dataset

    # Setter
    @multicell_dataset.setter
    def multicell_dataset(self, value):
        self._multicell_dataset = value

    # Column name
    # Getter
    @property
    def column_name(self):
        return self._column_name

    # Setter
    @column_name.setter
    def column_name(self, value):
        self._column_name = value
