#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

UNIT TESTING FOR CHART

"""

import chromaquant as cq
from openpyxl import Workbook
from openpyxl.chart import ScatterChart
from openpyxl.chart.shapes import GraphicalProperties

""" TEST CLASS """


class TestChart:

    # Test Chart creation with openpyxl
    def test_chart_init(self):

        # Create a new workbook
        wb = Workbook()

        # Get the default sheet
        ws = wb['Sheet']

        # Define some default data
        rows = [
            ['X', 'Y'],
            [1, 10],
            [2, 20],
            [3, 35],
            [4, 28],
            [5, 46]
        ]

        # Add the data to the worksheet
        for row in rows:
            ws.append(row)

        # Create a new Chart
        new_chart = \
            cq.Chart(ws, ScatterChart(), "'Sheet'!A2:A6", "'Sheet'!B2:B6")

        # Change properties
        cq.Theme()
        new_chart.base.varyColors = False
        new_chart.base.title = 'Chromatogram'
        new_chart.base.x_axis.title = 'RT (min)'
        new_chart.base.y_axis.title = 'Signal (a.u.)'
        new_chart.base.graphical_properties = GraphicalProperties()
        new_chart.base.graphical_properties.line.noFill = True
        new_chart.base.x_axis.majorGridlines = None
        new_chart.base.y_axis.majorGridlines = None
        new_chart.base.x_axis.minorGridlines = None
        new_chart.base.y_axis.minorGridlines = None
        # Add the chart to the worksheet
        ws.add_chart(new_chart.base, 'C5')

        # Save the workbook
        wb.save('./tests/unit/test_chart.xlsx')


test_chart = TestChart()
test_chart.test_chart_init()
