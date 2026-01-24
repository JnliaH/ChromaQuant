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

TOOLS FOR EXCEL REPORTING

Julia Hancock
Started 1-24-2025

"""

from openpyxl import Workbook
from pandas import ExcelWriter
from ..data import Table, Value

""" FUNCTIONS """


# Function to write a Table to Excel
def report_table(path: str,
                 table: Table,
                 writer: ExcelWriter):

    # Write the passed DataFrame to passed path
    table.data.to_excel(writer,
                        sheet_name=table.sheet,
                        startcol=table.start_column,
                        startrow=table.start_row,
                        index=False)

    return None


# Function to write a Value to Excel
def report_value(path: str,
                 value: Value,
                 workbook: Workbook,
                 value_nickname: str = ''):

    # Open the Value's sheet
    sheet = workbook[value.sheet]

    # If value nickname is an empty string...
    if value_nickname == '':
        # Write the Value's data to its start cell
        sheet.cell(value.start_row, value.start_column, value=value.data)

    # Otherwise...
    else:
        # Write the Value's name to its start cell
        sheet.cell(value.start_row, value.start_column, value=value_nickname)
        # Write the Value's data to the cell below
        sheet.cell(value.start_row + 1, value.start_column, value=value.data)

    return None
