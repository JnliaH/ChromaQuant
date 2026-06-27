#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

UNIT TESTING FOR CHART

"""

import chromaquant as cq
from openpyxl import Workbook
from openpyxl.chart import ScatterChart, BarChart

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

        # Add a theme to the Chart
        new_chart.theme = cq.Theme()

        # Change properties
        ws.add_chart(new_chart.base, 'C5')

        # Save the workbook
        wb.save('./tests/unit/test_chart.xlsx')


test_chart = TestChart()
test_chart.test_chart_init()
