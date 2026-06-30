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
from openpyxl.utils.cell import coordinate_from_string, \
                                column_index_from_string
from openpyxl import Workbook
from ..data._column_id import _ColumnID
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
    chart : ChartBase, optional
        The openpyxl chart (e.g., ScatterChart) to base this Chart off of,
        by default ChartBase()
    indep_column : _ColumnID, optional
        The ColumnID referencing a column in a Table or Breakdown to use for
        independent variable data (e.g., categories for BarChart), by default
        None
    data_columns : list[_ColumnID], optional
        A list of ColumnID's, each referencing a column in a Table or
        Breakdown to use for dependent variable data, by default []
    theme : Theme | None, optional
        The Theme to use in formatting the Chart, by default None
    titles_from_data : bool, optional
        Whether to use the first row in data ranges as Series titles, by
        default True
    anchor : str, optional
        The cell to anchor the chart to, by default 'C15'
    sheet : str, optional
        The worksheet to place the chart in, by default 'Sheet1'

    Raises
    ------
    ValueError:
        If passed anchor cell is not valid.
    ValueError:
        If sheet is set to a blank string.

    """

    # Init method
    def __init__(self,
                 chart: ChartBase = ChartBase(),
                 indep_column: _ColumnID = None,
                 data_columns: list[_ColumnID] = [],
                 theme: Theme | None = None,
                 titles_from_data: bool = True,
                 anchor: str = '',
                 sheet: str = ''
                 ):

        # Set the base chart
        self._base = chart

        # Set the range attributes
        self._indep_column = indep_column
        self._data_columns = data_columns

        # Set the theme if not None, otherwise set to None
        self.theme = theme if theme is not None else None

        # Set the titles_from_data attribute
        self._titles_from_data = titles_from_data

        # Set the anchor cell
        self._anchor = anchor if anchor != '' else 'C15'

        # Get the anchor cell's start column and row
        self.start_column, self.start_row = \
            self.get_cell_indices(self._anchor)

        # Set the sheet
        self._sheet = sheet if sheet != '' else 'Sheet1'

        # Set the default workbook
        self._workbook: Workbook = None

        # Update the chart
        self._update_series()

    """ PROPERTIES """
    # Anchor
    # Getter
    @property
    def anchor(self):
        """
        Get or set the anchor cell to report to.
        """
        return self._anchor

    # Setter
    @anchor.setter
    def anchor(self, value: str):
        # Try...
        try:
            # Get the cell's absolute indices
            self.start_column, self.start_row = self.get_cell_indices(value)
            # Set the starting cell
            self._anchor = value
        # If an exception occurs...
        except Exception as e:
            raise ValueError(f'Passed start cell is not valid: {e}')

    # Base chart
    # Getter
    @property
    def base(self):
        """
        Get or set the base openpyxl Chart object.
        """
        return self._base

    # Setter
    @base.setter
    def base(self, value):
        self._base = value

    # Independent range
    # Getter
    @property
    def indep_column(self):
        """
        Get, set, or delete the ColumnID for the independent axis.
        """
        return self._indep_column

    # Setter
    @indep_column.setter
    def indep_column(self, value: str):
        # Set the independent range
        self._indep_column = value
        # Update the chart
        self._update_series()

    # Deleter
    @indep_column.deleter
    def indep_column(self):
        self._indep_column = None
        # Update the chart
        self._update_series()

    # Independent reference
    # Getter
    @property
    def indep_reference(self):
        """
        Get the Reference for the current independent ColumnID.
        """
        # Get a range string
        range_string = \
            self._indep_column.multicell_dataset._reference[
                self._indep_column.column_name
                ]['range']
        # Get the worksheet
        worksheet = \
            self._indep_column.multicell_dataset._reference[
                self._indep_column.column_name
                ]['sheet']
        return Reference(worksheet=worksheet,
                         range_string=range_string)

    # Data ranges
    # Getter
    @property
    def data_columns(self):
        """
        Get, set, or delete the ColumnID's for the data series.
        """
        return self._data_columns

    # Setter
    @data_columns.setter
    def data_columns(self, value):
        self._data_columns = value
        # Update the chart
        self._update_series()

    # Deleter
    @data_columns.deleter
    def data_columns(self):
        self._data_columns = []
        # Update the chart
        self._update_series()

    # Data references
    # Getter
    @property
    def data_references(self):
        """
        Get the References for the current data ColumnID's.
        """
        # Get a list of range strings and worksheets
        reference_data = \
            [{'range_string': data_column.multicell_dataset._reference[
                data_column.column_name]['range'],
              'worksheet': data_column.multicell_dataset._reference[
                data_column.column_name]['sheet']}
             for data_column in self._data_columns]
        # Return a list of references
        return [Reference(worksheet=dict['worksheet'],
                          range_string=dict['range_string'])
                for dict in reference_data]

    # Sheet properties
    # Getter
    @property
    def sheet(self) -> str:
        """
        Get or set the name of the Excel worksheet to report to.
        """
        return self._sheet

    # Setter
    @sheet.setter
    def sheet(self, value: str):
        if value == '':
            raise ValueError('Chart sheet cannot be an empty string.')
        self._sheet = value

    # Theme
    # Getter
    @property
    def theme(self):
        """
        Get or set the Theme to use for this Chart.
        """
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

    # Titles from data
    # Getter
    @property
    def titles_from_data(self):
        """
        Get or set a boolean determining whether to get Series titles from
        data ranges.
        """
        return self._titles_from_data

    # Setter
    @titles_from_data.setter
    def titles_from_data(self, value: bool):
        self._titles_from_data = value

    """ METHODS """
    # Method to add a data column
    def add_data_column(self, column):
        """
        Method to add a data ColumnID to the list of data columns.

        Parameters
        ----------
        column : ColumnID
            Column to add to the current list of column data.

        Returns
        -------
        None

        """
        # Append the column to the data columns list
        self._data_columns.append(column)

        return None

    # Method to update the chart
    def _update_series(self):
        """
        Method to update the Series plotted in the Chart.

        Returns
        -------
        None

        """
        # Clear all existing series
        self._base.series.clear()

        # If both ranges are not blank...
        if self._indep_column and self._data_columns:

            # Get every column id's parent object's reference attribute
            all_references = [column.multicell_dataset.reference
                              for sublist in ((self._indep_column,),
                                              self._data_columns)
                              for column in sublist]

            # If all references are not empty...
            if all(all_references):

                # For every data column...
                for column_reference in self.data_references:

                    # If the chart is a ScatterChart...
                    if self._base.tagname == 'scatterChart':

                        # Create a Series
                        series = \
                            SeriesFactory(
                                column_reference,
                                self.indep_reference,
                                title_from_data=self._titles_from_data)

                        # Add the Series to the chart
                        self._base.series.append(series)

                    # Otherwise...
                    else:

                        # Add the data
                        self._base.add_data(
                            data=column_reference,
                            titles_from_data=self._titles_from_data
                            )

                        # Add the categories
                        self._base.set_categories(labels=self.indep_reference)

            # Otherwise, pass
            else:
                pass

        # Otherwise, pass
        else:
            pass

        return None

    # Method to update the theme
    def _update_theme(self):
        """
        Method to update the Chart Theme.

        Returns
        -------
        None

        """
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
        # Set x tick styles
        # NOTE: A None value results in no tick marks
        self._base.x_axis.majorTickMark = \
            self._chart_style.x_axis['tick_major_style']
        self._base.x_axis.minorTickMark = \
            self._chart_style.x_axis['tick_minor_style']
        # Set x tick units if not a TextAxis, otherwise pass
        try:
            self._base.x_axis.majorUnit = \
                self._chart_style.x_axis['tick_major_unit'] \
                if self._chart_style.x_axis['tick_major_unit'] is not None \
                else self._base.x_axis.majorUnit
            self._base.x_axis.minorUnit = \
                self._chart_style.x_axis['tick_minor_unit'] \
                if self._chart_style.x_axis['tick_minor_unit'] is not None \
                else self._base.x_axis.minorUnit
        except AttributeError:
            pass

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
        # Set y tick styles
        # NOTE: A None value results in no tick marks
        self._base.y_axis.majorTickMark = \
            self._chart_style.y_axis['tick_major_style']
        self._base.y_axis.minorTickMark = \
            self._chart_style.y_axis['tick_minor_style']
        # Set y tick units if not a TextAxis, otherwise pass
        try:
            self._base.y_axis.majorUnit = \
                self._chart_style.y_axis['tick_major_unit'] \
                if self._chart_style.y_axis['tick_major_unit'] is not None \
                else self._base.y_axis.majorUnit
            self._base.y_axis.minorUnit = \
                self._chart_style.y_axis['tick_minor_unit'] \
                if self._chart_style.y_axis['tick_minor_unit'] is not None \
                else self._base.y_axis.minorUnit
        except AttributeError:
            pass

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
