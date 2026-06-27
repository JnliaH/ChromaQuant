#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This submodule contains the Chart class definition.

"""

import logging
from openpyxl.chart._chart import ChartBase
from openpyxl.chart import Reference
from openpyxl.chart.series_factory import SeriesFactory
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.title import TitleDescriptor
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import ParagraphProperties, \
                                  CharacterProperties, \
                                  Font
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
                 theme: Theme | None = None
                 ):

        # Set the worksheet
        self._worksheet = worksheet

        # Set the base chart
        self._base = chart

        # Set the range attributes
        self._indep_range = indep_range
        self._data_range = data_range

        # Set the theme if not None, otherwise set to None
        self.theme = theme if theme is not None else None

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

        # Set the Theme
        self._theme = value

        # If the Theme is not None...
        if self._theme is not None:

            # Get the appropriate ChartStyle from the Theme using the base
            # chart tagname
            self._chart_style = getattr(self._theme, self._base.tagname)

            # Update the theme
            self._update_theme()

        # Otherwise, pass
        else:
            pass

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

    # Method to update the theme
    def _update_theme(self):

        # Function to set the font and overlay of a title
        def set_font_and_overlay(title_type: str,
                                 title: TitleDescriptor):

            # If the title is not None...
            if getattr(self._chart_style, title_type)['title'] is not None:

                # Set the title overlay
                title.overlay = \
                    getattr(self._chart_style, title_type)['overlay']

                # Create CharacterProperties
                char_props = CharacterProperties()

                # Set the latin if font name specified, otherwise pass
                char_props.latin = Font(
                    typeface=getattr(self._chart_style,
                                     title_type)['font_name']) \
                    if getattr(self._chart_style, title_type)['font_name'] \
                    is not None else char_props.latin

                # Set the size if size specified, otherwise pass
                char_props.sz = \
                    getattr(self._chart_style, title_type)['font_size']*100 \
                    if getattr(self._chart_style, title_type)['font_size'] \
                    is not None else char_props.sz

                # Set the title font
                title.tx.rich.p[0].pPr = ParagraphProperties(defRPr=char_props)

            # Otherwise, pass
            else:
                pass

            return None

        # Create the x-title CharacterProperties
        # CHART
        # Create GraphicalProperties
        self._base.graphical_properties = \
            GraphicalProperties()
        # Set varyColors
        self._base.varyColors = \
            self._chart_style.chart['vary_colors']
        # Set outline
        self._base.graphical_properties.line.noFill = \
            not self._chart_style.chart['chart_outline']
        # Set rounded corners
        self._base.roundedCorners = \
            self._chart_style.chart['rounded_corners']

        # TITLE
        # Set the title value
        self._base.title = \
            self._chart_style.title['title'] \
            if self._chart_style.title['title'] is not None \
            else self._base.title

        # Set the title font and overlay
        set_font_and_overlay('title', self._base.title)

        # X-AXIS
        # Set the gridlines to None if drawing is set to False
        if not self._chart_style.x_axis['draw_major_grid']:
            self._base.x_axis.majorGridlines = None
        if not self._chart_style.x_axis['draw_minor_grid']:
            self._base.x_axis.minorGridlines = None
        # Set the numbers display setting
        self._base.x_axis.delete = not self._chart_style.x_axis['show_numbers']
        # Set the title value
        self._base.x_axis.title = \
            self._chart_style.x_axis['title'] \
            if self._chart_style.x_axis['title'] is not None \
            else self._base.x_axis.title
        # Set the title font and overlay
        set_font_and_overlay('x_axis', self._base.x_axis.title)
        # Set major x ticks
        self._base.x_axis.majorTickMark = \
            self._chart_style.x_axis['tick_major_style'] \
            if self._chart_style.x_axis['tick_major_style'] is not None \
            else self._base.x_axis.majorTickMark
        self._base.x_axis.majorUnit = \
            self._chart_style.x_axis['tick_major_unit'] \
            if self._chart_style.x_axis['tick_major_unit'] is not None \
            else self._base.x_axis.majorUnit
        # Set minor x ticks
        self._base.x_axis.minorTickMark = \
            self._chart_style.x_axis['tick_minor_style'] \
            if self._chart_style.x_axis['tick_minor_style'] is not None \
            else self._base.x_axis.minorTickMark
        self._base.x_axis.minorUnit = \
            self._chart_style.x_axis['tick_minor_unit'] \
            if self._chart_style.x_axis['tick_minor_unit'] is not None \
            else self._base.x_axis.minorUnit

        # Y-AXIS
        # Set the gridlines to None if drawing is set to False
        if not self._chart_style.y_axis['draw_major_grid']:
            self._base.y_axis.majorGridlines = None
        if not self._chart_style.y_axis['draw_minor_grid']:
            self._base.y_axis.minorGridlines = None
        # Set the numbers display setting
        self._base.y_axis.delete = not self._chart_style.y_axis['show_numbers']
        # Set the title value
        self._base.y_axis.title = \
            self._chart_style.y_axis['title'] \
            if self._chart_style.y_axis['title'] is not None \
            else self._base.y_axis.title
        # Set the title font and overlay
        set_font_and_overlay('y_axis', self._base.y_axis.title)
        # Set major y ticks
        self._base.y_axis.majorTickMark = \
            self._chart_style.y_axis['tick_major_style'] \
            if self._chart_style.y_axis['tick_major_style'] is not None \
            else self._base.y_axis.majorTickMark
        self._base.y_axis.majorUnit = \
            self._chart_style.y_axis['tick_major_unit'] \
            if self._chart_style.y_axis['tick_major_unit'] is not None \
            else self._base.y_axis.majorUnit
        # Set minor y ticks
        self._base.y_axis.minorTickMark = \
            self._chart_style.y_axis['tick_minor_style'] \
            if self._chart_style.y_axis['tick_minor_style'] is not None \
            else self._base.y_axis.minorTickMark
        self._base.y_axis.minorUnit = \
            self._chart_style.y_axis['tick_minor_unit'] \
            if self._chart_style.y_axis['tick_minor_unit'] is not None \
            else self._base.y_axis.minorUnit

        # PLOT AREA
        # If draw_outline is true...
        if self._chart_style.plot_area['draw_outline']:
            # Create a plot area line style
            plot_area_line = LineProperties()
            # Apply the width if provided, otherwise pass
            plot_area_line.w = \
                self._chart_style.plot_area['outline_width']*10000 \
                if self._chart_style.plot_area['outline_width'] is not None \
                else plot_area_line.w
            # Apply the outline style if provided, otherwise pass
            plot_area_line.cmpd = \
                self._chart_style.plot_area['outline_style'] \
                if self._chart_style.plot_area['outline_style'] is not None \
                else plot_area_line.cmpd
            # Apply the outline color if provided, otherwise pass
            plot_area_line.solidFill = \
                self._chart_style.plot_area['outline_color'] \
                if self._chart_style.plot_area['outline_color'] is not None \
                else plot_area_line.solidFill
            # Apply the style to the plot area outline
            self._base.plot_area.spPr = GraphicalProperties(ln=plot_area_line)
        # Otherwise, pass
        else:
            pass

        # LEGEND
        # Apply the position if provided, otherwise pass
        self._base.legend.position = \
            self._chart_style.legend['position'] \
            if self._chart_style.legend['position'] is not None \
            else self._base.legend.position
        # Apply the overlay if provided, otherwise pass
        self._base.legend.overlay = \
            self._chart_style.legend['overlay'] \
            if self._chart_style.legend['overlay'] is not None \
            else self._base.legend.overlay

        return None
