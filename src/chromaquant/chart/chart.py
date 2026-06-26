#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This submodule contains the Chart class definition.

"""

import logging
from openpyxl.chart._chart import ChartBase
from openpyxl.chart import Reference
from openpyxl.chart.series_factory import SeriesFactory
from openpyxl.worksheet.worksheet import Worksheet
from ..logging_and_handling import setup_logger, setup_error_logging
from ..theme import Theme

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)

""" CLASS """


# Define the Chart class
class Chart:
    """
    Chart objects enable the creation of charts in Results Excel reports.

    Parameters
    ----------

    Raises
    ------

    """

    # Init method
    def __init__(self,
                 worksheet: Worksheet = None,
                 chart: ChartBase = ChartBase(),
                 indep_range: str = '',
                 data_range: str = '',
                 theme: Theme = Theme()
                 ):

        # Set the worksheet
        self._worksheet = worksheet

        # Set the base chart
        self._base = chart

        # Set the range attributes
        self._indep_range = indep_range
        self._data_range = data_range

        # Set the theme
        self._theme = theme

        # Update the chart
        self._update_series()

    """ PROPERTIES """
    # Base chart
    # Getter
    @property
    def base(self):
        return self._base

    # Setter
    @base.setter
    def base(self, value):
        self._base = value

    # Independent range
    # Getter
    @property
    def indep_range(self):
        return self._indep_range

    # Setter
    @indep_range.setter
    def indep_range(self, value: str):
        # Set the independent range
        self._indep_range = value
        # Update the chart
        self._update_series()

    # Deleter
    @indep_range.deleter
    def indep_range(self):
        self._indep_range = ''
        # Update the chart
        self._update_series()

    # Independent reference
    # Getter
    @property
    def indep_reference(self):
        return Reference(worksheet=self._worksheet,
                         range_string=self._indep_range)

    # Data range
    # Getter
    @property
    def data_range(self):
        return self._data_range

    # Setter
    @data_range.setter
    def data_range(self, value: str):
        self._data_range = value
        # Update the chart
        self._update_series()

    # Deleter
    @data_range.deleter
    def data_range(self):
        self._data_range = ''
        # Update the chart
        self._update_series()

    # Data reference
    # Getter
    @property
    def data_reference(self):
        return Reference(worksheet=self._worksheet,
                         range_string=self._data_range)

    # Worksheet
    # Getter
    @property
    def worksheet(self):
        return self._worksheet

    # Setter
    @worksheet.setter
    def worksheet(self, value):
        self._worksheet = value
        # Update the chart
        self._update_series()

    # Deleter
    @worksheet.deleter
    def worksheet(self):
        self._worksheet = None
        # Update the chart
        self._update_series()

    # Theme
    # Getter
    @property
    def theme(self):
        return self._theme

    # Setter
    @theme.setter
    def theme(self, value):
        self._theme = value

    """ METHODS """
    # Method to create the chart object
    def _create_chart(self):

        # Create the chart object
        self.chart = self.chart_types[self.type]['obj']()

        # Define the chart axis type
        self.axis_type = self.chart_types[self.type]['axis_type']

        return None

    # Method to update the chart
    def _update_series(self):

        # Clear all existing series
        # self._base.series.clear()

        # If the ranges are not blank...
        if self._indep_range and self._data_range:

            # Get the independent and data references
            indep_reference = self.indep_reference
            data_reference = self.data_reference

            # For every column in the data range...
            for column_reference in data_reference.cols:

                # Create a Series
                series = \
                    SeriesFactory(column_reference,
                                  indep_reference)

                # Chart
                # Add the Series to the chart
                self._base.series.append(series)

        # Otherwise, pass
        else:
            pass

        return None
