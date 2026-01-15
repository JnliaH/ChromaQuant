#!/usr/bin/env python
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2025, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SUBPACKAGE FOR MATCHING DATAFRAME ROWS ACCORDING TO A PASSED MODEL

Julia Hancock
Started 11/13/2025

"""

""" FUNCTIONS """


# Function that matches one DataFrame's values to another using some comparison
def match_dataframes(main_DF, second_DF, match_dict, match_config):

    # Function that adds data from one row to another
    def add_to_first(first, second, add_columns):

        # Create a copy of the passed first_row
        new_first = first.copy()

        # For every column in add_columns...
        for column in add_columns:
            # Set the first row's entry to the second row's entry
            new_first.at[column] = second[column]

        return new_first

    # Function that searches through the second_DF
    # for a match to one row in the main_DF
    def match_one_row(main_row, second_DF, match_dict, match_config):

        # Create a copy of the passed main_row
        new_main_row = main_row.copy()

        # Get the comparison value from the new main row
        main_comp_value = new_main_row[match_dict['local_comparison']]

        # Get the import_include_columns
        import_include_col = match_config['import_include_col']

        # Get the comparison header of the second_DF
        second_comp_header = match_dict['import_comparison']

        # Get the comparison function
        comp_func = match_config['match_comparison_function']

        # Transform the comparison value into a form expected in the second_DF
        transform_main_comp_value = comp_func(main_comp_value)

        # Get a slice of the second dataframe where main_comp_value
        # is present in the second dataframe's comparison column
        second_DF_matches = \
            second_DF.loc[second_DF[second_comp_header] ==
                          transform_main_comp_value].copy()

        # If the slice is empty...
        if second_DF_matches.empty:

            # Try to get a slice of the second dataframe where the transformed
            # main comparison value is between the specified error margins
            try:
                # Define upper and lower limits
                transform_main_max = \
                    transform_main_comp_value + \
                    match_config['match_comparison_error']
                transform_main_min = \
                    transform_main_comp_value - \
                    match_config['match_comparison_error']
                # Get a slice
                second_DF_matches = \
                    second_DF.loc[(second_DF[second_comp_header]
                                   >= transform_main_min) &
                                  (second_DF[second_comp_header]
                                   <= transform_main_max)].copy()

                # If the slice has more than one row...
                if len(second_DF_matches) > 1:

                    # Add an error to each row
                    second_DF_matches['cq__error'] = \
                        (second_DF_matches[second_comp_header] -
                            match_config['match_comparison_error'])

                    # Get the index of the row with the smallest error
                    min_error_index = second_DF_matches['cq__error'].idxmin()
                    second_best_row = second_DF_matches.loc[min_error_index]

                    new_main_row = \
                        add_to_first(new_main_row,
                                     second_best_row,
                                     import_include_col)

                # Otherwise, if the slice contains exactly one row...
                elif len(second_DF_matches) == 1:

                    # Set the new main row to that single row in
                    # second_DF_matches
                    new_main_row = \
                        add_to_first(new_main_row,
                                     second_DF_matches.loc[
                                      second_DF_matches.index.min()],
                                     import_include_col)

                # Otherwise, pass
                else:
                    pass

                # If this does not work, pass
                # NOTE: This is intended to catch cases where comparison
                # values are non-numbers
            except Exception:
                pass

        # Otherwise...
        else:

            # Set the new main row to the first row in second_DF_matches
            # NOTE: This means that exact duplicates are resolved by picking
            # the one with the first index in second_DF_matches!
            new_main_row = \
                add_to_first(new_main_row,
                             second_DF_matches.loc[
                                 second_DF_matches.index.min()],
                             import_include_col)

        return new_main_row

    # Create a copy of the passed DataFrame
    new_main_DF = main_DF.copy()

    # For every row in the main dataframe...
    for i, row in main_DF.iterrows():

        # Get the output of the match_one_row function for that row
        new_row = \
            match_one_row(row, second_DF, match_dict, match_config)

        new_main_DF.loc[i] = new_row

    return new_main_DF
