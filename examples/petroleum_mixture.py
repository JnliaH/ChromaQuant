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

""" PATHS """

# Define paths for example data
path_FID_integration = \
    './examples/example_data/example_liquid_FID_integration.csv'
path_MS_components = \
    './examples/example_data/example_MS_components.csv'

""" DATASET CREATION """

# Create a table for integration results from a Flame Ionization Detector
# signal collected when analyzing a liquid sample
lq_FID_integration = cq.Table()
# Read a .csv to add data to this table
lq_FID_integration.import_csv_data(path_FID_integration)

# Create a table for a liquid components table from a Mass Spectrometer
lq_MS_components = cq.Table()
# Read a .csv to add data to this table
lq_MS_components.import_csv_data(path_MS_components)

""" MATCHING """

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

# Create a new liquids table with the match results
liquids = cq.Table(lq_FIDpMS)

# Add a carbon number count column
liquids.add_element_count_column('Formula', 'C', 'Carbon Number')

print(liquids)
