#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Copyright (c) 2026, by Julia Hancock
License: BSD 3-Clause License

UNIT TESTING FOR HITFILTER

"""

import chromaquant as cq

""" TEST CLASS """


class TestHitFilter:

    # Test HitFilter creation and property methods
    def test_attributes(self):

        # Create empty tests list
        tests = []

        # Create HitFilter object, assigning attributes
        hit_filter = cq.HitFilter(
            peak_rt_error=0.001,
            no_bar=[],
            soft_bar=[],
            do_show_previous_matches=True
        )

        # Create elements
        element_1 = cq.Element('C', 2)
        element_2 = cq.Element('H', 1)
        element_3 = cq.Element('O', 10)
        element_4 = cq.Element('N', 5)

        # Check peak_rt_error property
        # Check that peak_rt_error is 0.001
        tests.append(
            True if hit_filter.peak_rt_error == 0.001
            else False
        )
        # Delete peak_rt_error
        del hit_filter.peak_rt_error
        # Check that peak_rt_error is 0
        tests.append(
            True if hit_filter.peak_rt_error == 0
            else False
        )
        # Set peak_rt_error
        hit_filter.peak_rt_error = 0.002
        # Check that peak_rt_error is 0.002
        tests.append(
            True if hit_filter.peak_rt_error == 0.002
            else False
        )

        # Check no_bar property
        # Add one element to no_bar
        hit_filter.no_bar.append(element_1)
        # Check that no_bar has one element
        tests.append(
            True if len(hit_filter.no_bar) == 1
            else False
            )
        # Delete no_bar
        del hit_filter.no_bar
        # Check that no_bar is an empty list
        tests.append(
            True if not hit_filter.no_bar
            else False
        )
        # Set no_bar
        hit_filter.no_bar = [element_1, element_2]
        # Check that no_bar's first element is 'C' and second element is 'H'
        tests.append(
            True if hit_filter.no_bar[0].symbol == 'C'
            and hit_filter.no_bar[1].symbol == 'H'
            else False
            )
        # Check that no_bar's first priority is 2 and second priority is 1
        tests.append(
            True if hit_filter.no_bar[0].priority == 2
            and hit_filter.no_bar[1].priority == 1
            else False
            )

        # Check soft_bar property
        # Add one element to soft_bar
        hit_filter.soft_bar.append(element_3)
        # Check that soft_bar has one element
        tests.append(
            True if len(hit_filter.soft_bar) == 1
            else False
            )
        # Delete soft_bar
        del hit_filter.soft_bar
        # Check that soft_bar is an empty list
        tests.append(
            True if not hit_filter.soft_bar
            else False
        )
        # Set soft_bar
        hit_filter.soft_bar = [element_3, element_4]
        # Check that soft_bar's first element is 'O' and second element is 'N'
        tests.append(
            True if hit_filter.soft_bar[0].symbol == 'O'
            and hit_filter.soft_bar[1].symbol == 'N'
            else False
            )
        # Check that soft_bar's first priority is 10 and second priority is 5
        tests.append(
            True if hit_filter.soft_bar[0].priority == 10
            and hit_filter.soft_bar[1].priority == 5
            else False
            )

        # Assert all test results
        assert all(tests)

    # Test the application of HitFilter on an example table
    def test_filter_table(self):

        # Create empty tests list
        tests = []

        # Create a Table
        table = cq.Table()

        # Import .csv data
        table.import_csv_data('./tests/unit/test_hit_filter.csv')

        # Create a HitFilter
        hit_filter = cq.HitFilter(
            peak_rt_error=0.005,
            no_bar=[cq.Element('C', 1), cq.Element('H', 1)],
            soft_bar=[cq.Element('O', 2), cq.Element('N', 1)],
            do_show_previous_matches=True
        )

        # Constrain the Table data
        hit_filter.constrain(
            table=table,
            rt_column=table.column_id('Component RT'),
            compound_column=table.column_id('Compound Name'),
            formula_column=table.column_id('Formula'),
            ranking_column=table.column_id('Match Factor')
        )

        # Get an empty list of test rows
        test_rows = []
        # Get the rows at indices 84, 136, 183
        test_rows.append(table.data.iloc[84, :])
        test_rows.append(table.data.iloc[136, :])
        test_rows.append(table.data.iloc[183, :])

        # Get the expected values for the test rows
        expected_vals = [
            ['C12H22', 'C9H18O', 'C8H14O'],
            ['C23H20O4', 'C10H9NO3', 'C17H20O4'],
            ['C11H16', 'C14H23N', 'C18H31N']
            ]

        # For every test row...
        for i, row in enumerate(test_rows):
            tests.append(
                True
                if row['Formula'] == expected_vals[i][0]
                and row['Previous Best Formula'] == expected_vals[i][1]
                and row['Previous Worst Formula'] == expected_vals[i][2]
                else False
            )

        assert all(tests)
