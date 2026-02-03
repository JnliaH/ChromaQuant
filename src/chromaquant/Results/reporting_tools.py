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
from openpyxl.styles import Alignment
from pandas import ExcelWriter
from ..data import Breakdown, Table, Value
from ..data.dataset import DataSet

""" FUNCTIONS """


# Function to write a Breakdown to Excel
def report_breakdown(breakdown: Breakdown,
                     writer: ExcelWriter):

    # Get the start row based on whether there is a header or not
    start_row = \
        breakdown.start_row if breakdown.header == '' \
        else breakdown.start_row + 1

    # Write the passed DataFrame to passed path
    breakdown.data.to_excel(writer,
                            sheet_name=breakdown.sheet,
                            startcol=breakdown.start_column,
                            startrow=start_row,
                            index=False)


# Function to write a header to Excel
def report_header(dataset: DataSet,
                  workbook: Workbook):

    # If the dataset has a blank header...
    if dataset.header == '':
        # Don't report header
        return None

    # If dataset's sheet does not exist in workbook...
    if dataset.sheet not in workbook.sheetnames:
        # Create it
        workbook.create_sheet(dataset.sheet)

    # Open the dataset's sheet
    sheet = workbook[dataset.sheet]

    # Write the header to the start cell (adjusted from absolute)
    cell = sheet.cell(dataset.start_row + 1,
                      dataset.start_column + 1,
                      value=dataset.header)

    # Center the header cell
    cell.alignment = Alignment(horizontal='center')

    # Try to get the number of columns in the DataSet's data,
    # only working for Table, Breakdown
    try:
        num_cols = dataset.data.shape[1]

        # If this works, merge the header cell with adjacent cells
        # to center the header across the DataFrame
        sheet.merge_cells(start_row=dataset.start_row + 1,
                          start_column=dataset.start_column + 1,
                          end_row=dataset.start_row + 1,
                          end_column=dataset.start_column + num_cols)

    # If this does not work, pass
    except AttributeError:
        pass

    return None


# Function to write a Table to Excel
def report_table(table: Table,
                 writer: ExcelWriter):

    # Get the start row based on whether there is a header or not
    start_row = \
        table.start_row if table.header == '' \
        else table.start_row + 1

    # Write the passed DataFrame to passed path
    table.data.to_excel(writer,
                        sheet_name=table.sheet,
                        startcol=table.start_column,
                        startrow=start_row,
                        index=False)

    return None


# Function to write a Value to Excel
def report_value(value: Value,
                 workbook: Workbook):

    # If Value's sheet does not exist in workbook...
    if value.sheet not in workbook.sheetnames:
        # Create it
        workbook.create_sheet(value.sheet)

    # Open the Value's sheet
    sheet = workbook[value.sheet]

    # Get the start row based on whether there is a header or not
    start_row = \
        value.start_row + 1 if value.header == '' \
        else value.start_row + 2

    # Write the Value's data to the cell below, adjusting from absolute
    sheet.cell(start_row,
               value.start_column + 1,
               value=value.data)

    return None
