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

Example analysis for a petroleum mixture

Julia Hancock
Started 01-27-2026

"""

import chromaquant as cq
import json

""" PATHS """

# Define paths for example data
path_lq_FID_integration = \
    './examples/example_data/example_liquid_FID_integration.csv'
path_lq_MS_components = \
    './examples/example_data/example_MS_components.csv'
path_lq_FID_RFs = \
    './examples/example_data/example_FID_response_factors.csv'

""" SHEETS AND CELLS """
# Define sheets for liquids
liquid_sheet = 'Liquids Analysis'

# Define starting cells for liquid tables and values
liquid_table_cell = '$B$5'
liquid_IS_area_cell = '$B$2'
liquid_IS_mass_cell = '$C$2'
liquid_breakdown_cell = '$P$5'
liquid_2D_breakdown_cell = '$P$10'

""" GETTING CONFIGURATION FROM FILE """

# Read example_config.json
with open('./examples/example_data/example_config.json', 'r') as config_file:
    config_dict = json.load(config_file)

""" DATASET CREATION """
# Create a table for integration results from a Flame Ionization Detector
# signal collected when analyzing a liquid sample
lq_FID_integration = cq.Table()
# Read a .csv to add data to this table
lq_FID_integration.import_csv_data(path_lq_FID_integration)

# Create a table for a liquid components table from a Mass Spectrometer
lq_MS_components = cq.Table()
# Read a .csv to add data to this table
lq_MS_components.import_csv_data(path_lq_MS_components)

# Create a table for liquid response factors
lq_FID_RF = cq.Table()
# Read a .csv to add data to this table
lq_FID_RF.import_csv_data(path_lq_FID_RFs)

# Create values for the internal standard area and mass
IS_area = cq.Value(sheet=liquid_sheet,
                   start_cell=liquid_IS_area_cell,
                   header='Internal Standard Area')
IS_mass = cq.Value(data=30,
                   sheet=liquid_sheet,
                   start_cell=liquid_IS_mass_cell,
                   )
# header='Internal Standard Mass (mg)'
# Create a table for liquids analysis
liquids_table = cq.Table(sheet='Liquids Analysis',
                         start_cell='$B$5')

# Create a 1D breakdown by carbon number
liquids_CN_breakdown = cq.Breakdown(liquid_breakdown_cell,
                                    'Liquids Analysis')

# Create a 2D breakdown for liquids
liquids_2D_breakdown = cq.Breakdown(liquid_2D_breakdown_cell,
                                    'Liquids Analysis')

""" MATCHING FID TO MS """
# Create a match configuration for liquids FID-MS
match_config_lq_FIDpMS = cq.MatchConfig()

# Add a match condition
match_config_lq_FIDpMS.add_match_condition(condition=cq.MatchConfig.IS_EQUAL,
                                           comparison=['RT', 'Component RT'],
                                           error=0.05)

# Add columns to include from second DataFrame
match_config_lq_FIDpMS.import_include_col = ['Component RT',
                                             'Compound Name',
                                             'Formula',
                                             'Match Factor']

# Specify which columns to output
match_config_lq_FIDpMS.output_cols_dict = {'RT': 'FID RT (min)',
                                           'Area': 'Area',
                                           'Component RT': 'MS RT (min)',
                                           'Compound Name': 'Compound',
                                           'Formula': 'Formula',
                                           'Match Factor': 'Match Factor'}

# Add a multple hits rule to select the lowest error
match_config_lq_FIDpMS.multiple_hits_rule = cq.MatchConfig.SELECT_HIGHEST_VALUE

# Set the multiple hits rule column to the comparison column
match_config_lq_FIDpMS.multiple_hits_column = 'Match Factor'

# Match liquid FID and MS data
lq_FIDpMS = lq_FID_integration.match(lq_MS_components.data,
                                     match_config_lq_FIDpMS)

# Set results to liquids_table data attribute
liquids_table.data = lq_FIDpMS

""" ADDING CARBON NUMBER AND MOLECULAR WEIGHT """

# Add a carbon number count column
liquids_table.add_element_count_column('Formula', 'C', 'Carbon Number')

# Add a molecular weight column
liquids_table.add_molecular_weight_column('Formula', 'Molecular Weight')

""" MATCHING RESPONSE FACTORS """

# Create a match configuration for liquid response factors
match_config_lq_RF = cq.MatchConfig()

# Add a match condition
match_config_lq_RF.add_match_condition(condition=cq.MatchConfig.IS_EQUAL,
                                       comparison='Compound')

# Add columns to include from second DataFrame
match_config_lq_RF.import_include_col = ['Sample Set', 'Response Factor']

# Match response factors to liquids FIDpMS
liquids_table.data = liquids_table.match(lq_FID_RF.data,
                                         match_config_lq_RF)

""" ASSIGNING INTERPOLATED RESPONSE FACTORS """


# Define a function for assigning interpolated response factors
def RF_by_carbon_number(CN):
    return 0.0000496*CN**3 - 0.003*CN**2 + 0.0506*CN + 0.731


# For every row in the liquids data...
for i, row in liquids_table.data.iterrows():

    # If the Response Factor is None...
    if row['Response Factor'] is None:

        # Get the carbon number
        CN = row['Carbon Number']

        # If the carbon number is not zero...
        if CN != 0:

            # Get an interpolated response factor
            RF = RF_by_carbon_number(CN)

            # Set the row's response factor to RF
            liquids_table.data.at[i, 'Response Factor'] = RF

            # Set the row's Sample Set to Interpolated
            liquids_table.data.at[i, 'Sample Set'] = 'Interpolated'

        # Otherwise, pass
        else:
            pass

    # Otherwise, pass
    else:
        pass

""" ADDING COMPOUND TYPES """

# Create new Categories instance
hydrocarbon_categories = cq.utils.Categories()

# Get a dictionary of abbreviations and compound types
compound_type_dict = {'A': 'Aromatics',
                      'E': 'Alkenes',
                      'C': 'Cycloalkanes',
                      'B': 'Branched Alkanes',
                      'L': 'Linear Alkanes'}

# Add categories for each compound type
for abbreviation in compound_type_dict:
    hydrocarbon_categories[compound_type_dict[abbreviation]] = \
        config_dict[abbreviation]

# Set the categorizer function
hydrocarbon_categories.categorizer = hydrocarbon_categories.IS_IN

# Add compound types to the liquids table
liquids_table.add_category_column('Compound',
                                  hydrocarbon_categories,
                                  'Compound Type')

""" ADDING DATA TO RESULTS """
# Define Results instance for liquids analysis
liquids = cq.Results()

# Add the liquids table
liquids.add_table(liquids_table)

# Add the internal standard values
liquids.add_value(IS_area)
liquids.add_value(IS_mass)

# Add the liquids carbon number breakdown
liquids.add_breakdown(liquids_CN_breakdown)

# Add the liquids 2D breakdown
liquids.add_breakdown(liquids_2D_breakdown)

""" QUANTIFICATION """

# Create a formula string for the area cell
IS_area_formula_string = (f"=INDEX({liquids_table.insert('Area')}, MATCH("
                          f'"Hexane, 3-methyl-", '
                          f"{liquids_table.insert('Compound')}, 0))")

# Create a Formula instance for the area cell
IS_area_formula = cq.Formula(IS_area_formula_string)

# Add pointers to Formula
IS_area_formula.point_to(IS_area.id)

# Add the area cell Formula to liquids analysis
liquids.add_formula(IS_area_formula)

# Create an area ratio Formula
area_ratio_formula = cq.formula.FORMULA_IF_ERROR(
    cq.formula.FORMULA_DIVISION(
        liquids_table.insert('Area'),
        IS_area.insert()
    )
)

# Add pointers to Formula
area_ratio_formula.point_to('Ai/As', liquids_table.id)

# Add the area ratio Formula to the liquids analysis
liquids.add_formula(area_ratio_formula)

# Create a mass Formula
mass_formula = cq.formula.FORMULA_IF_ERROR(
    cq.formula.FORMULA_MULTIPLICATION(
        IS_mass.insert(),
        cq.formula.FORMULA_DIVISION(
            liquids_table.insert('Ai/As'),
            liquids_table.insert('Response Factor')
        ).formula_string,
        'Mass (mg)',
        liquids_table.id
    )
)

# Add the mass Formula to the liquids analysis
liquids.add_formula(mass_formula)

# Define carbon numbers to cover
CN_range = [1, 2, 3, 4, 5, 6, 7, 8]

# Create a 1D carbon number breakdown
liquids_CN_breakdown.create_1D(liquids_table,
                               'Carbon Number',
                               'Mass (mg)',
                               CN_range)

# Create a 2D carbon number-compound breakdown
liquids_2D_breakdown.create_2D(liquids_table,
                               'Compound Type',
                               'Carbon Number',
                               'Mass (mg)',
                               {'Carbon Number':
                                CN_range,
                                'Compound Type':
                                list(compound_type_dict.values())})

# Try to change the header of the breakdown
liquids_2D_breakdown.header = 'Distribution Matrix'

# Change the header of the liquids analysis table
liquids_table.header = 'Liquids Analysis'

# Change the header of the internal standard mass
IS_mass.header = 'Internal Standard Mass (mg)'

# Export the results to .csv
liquids.report_results('./examples/example_data/report.xlsx')
