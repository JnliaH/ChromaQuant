#!/usr/bin/env python
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

CLASS DEFINITION FOR MULTIPLE MATCH HITS RULE

Julia Hancock
Started 01-27-2025

"""

import pandas as pd
from collections.abc import Callable, Any

""" CLASS """


class MatchHitsRule:

    # Initialize
    def __init__(self,
                 callable: Callable[[pd.DataFrame], pd.Series] = None,
                 **kwargs):

        # Create attribute for callable
        self.callable = \
            callable if callable is not None else self.SELECT_FIRST_ROW

        # Create keyword arguments for all other passed kwargs
        self.__dict__.update(kwargs)

    # Method that gets the first row of a slice, used as the default
    # method of selecting one row of a slice that meets match conditions
    def SELECT_FIRST_ROW(self, DF: pd.DataFrame):

        # Get the first row of the DataFrame
        first_row = DF.loc[DF.index.min()]

        return first_row

    # Method that gets the error between an expected value and the actual
    # value for each row in a slice, selecting the row with the smallest error
    @staticmethod
    def SELECT_LOWEST_ERROR(self, DF: pd.DataFrame):

        # For each row in the slice...
        for i, row in DF.iterrows():
            # Define an error column as the difference between
            # the actual and expected valuese for a column
            DF.at[i, 'CQ Error'] = abs(DF.at[i, self.column_name] - self.expected_value)
