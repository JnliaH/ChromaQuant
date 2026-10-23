"""

HitFilter is used to apply a basic, chemical-element-based filter to a Table containing
compound best hits sorted by retention time.

"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from ..data import Table
    from ..data._column_id import _ColumnID

from .element import Element

""" CLASS """


# Class for Elements to enable compound constraints
class HitFilter:
    """
    Class that is used to filter a compound hit list based on the Elements present in
    each compound formula.

    Parameters
    ----------
    peak_rt_error : float, optional
        The allowable error between compound hit retention times within which hits must
        be filtered to give one best hit. Must be in the same units as the peak
        retention time (e.g., minutes). By default 0

    no_bar : list[Element], optional
        Elements that are always allowed in compound hits, regardless of priority.
        By default []

    soft_bar : list[Element], optional
        Elements that will be allowed in a best hit if there are no compound matches
        with only allowed Elements. Element priority is used to select one or more
        allowable elements before others. By default []

    """

    def __init__(
        self,
        peak_rt_error: float = 0,
        no_bar: list[Element] = [],
        soft_bar: list[Element] = [],
        do_show_previous_matches: bool = True,
    ):

        # Set initial property attributes
        self._peak_rt_error = peak_rt_error
        self._no_bar = no_bar
        self._soft_bar = soft_bar

        # Set other attributes
        self.do_show_previous_matches = do_show_previous_matches

    """ PROPERTIES """

    # Peak retention time error
    # Getter
    @property
    def peak_rt_error(self):
        return self._peak_rt_error

    # Setter
    @peak_rt_error.setter
    def peak_rt_error(self, value):
        self._peak_rt_error = value

    # Deleter
    @peak_rt_error.deleter
    def peak_rt_error(self):
        self._peak_rt_error = 0

    # NoBar (allowed elements)
    # Getter
    @property
    def no_bar(self):
        return self._no_bar

    # Setter
    @no_bar.setter
    def no_bar(self, value):
        self._no_bar = value

    # Deleter
    @no_bar.deleter
    def no_bar(self):
        self._no_bar = []

    # SoftBar (conditionally allowed elements)
    # Getter
    @property
    def soft_bar(self):
        return self._soft_bar

    # Setter
    @soft_bar.setter
    def soft_bar(self, value):
        self._soft_bar = value

    # Deleter
    @soft_bar.deleter
    def soft_bar(self):
        self._soft_bar = []

    """ STATIC METHODS """

    # Method to add match data to dataframe
    @staticmethod
    def _concat_df(
            data_slice: pd.Series,
            df_in: pd.DataFrame,
            out_columns: list[_ColumnID]
            ):
        """
        Method that adds best hit match data to the best hit DataFrame

        Parameters
        ----------
        data_slice : pandas.Series
            Series containing best hit match data for one retention time.
        df_in : pandas.DataFrame
            DataFrame containing prior best hit match data or no match data.
        out_columns: list of _ColumnID
            List of columns to include in df_out.

        Returns
        -------
        df_out: pandas.DataFrame
            DataFrame containing prior and current best hit match data.

        """

        # Get a list of data slice values
        list_out = [data_slice[out_columns[i]] for i in range(len(out_columns))]

        # Make a data slice dataframe and reindex it
        data_slice_df = pd.DataFrame([list_out], columns=out_columns)

        # Get the output dataframe
        df_out = pd.concat(
            [data_slice_df.astype(object), df_in.astype(object)], ignore_index=True
        )

        return df_out

    # Method to add series of matches with best and worst match factor to a
    # selected match series
    @staticmethod
    def _concat_series(
        data_slice: pd.Series,
        best_slice: pd.Series,
        worst_slice: pd.Series,
        columns: list[_ColumnID]
    ):
        """
        Method that records previous best and worst hits by concatenating them to the
        current best hit Series.

        Parameters
        ----------
        data_slice : pandas.Series
            Current best hit Series.
        best_slice : pandas.Series
            Previous best hit Series.
        worst_slice : pandas.Series
            Previous worst hit Series.
        columns : list of _ColumnID
            List of columns to include in return_slice.

        Returns
        -------
        return_slice: pd.Series
            Series containing best, previous best, and previous worst hits for a given
            retention time.

        """

        # Define dictionaries of new index names for bestSlice and worstSlice
        best_index = {
            f"{column.column_name}": f"Previous Best {column.column_name}"
            for column in columns
            }
        worst_index = {
            f"{column.column_name}": f"Previous Worst {column.column_name}"
            for column in columns
            }

        # Rename bestSlice and worstSlice indices
        best_slice = best_slice.copy()
        worst_slice = worst_slice.copy()
        best_slice.rename(index=best_index, inplace=True)
        worst_slice.rename(index=worst_index, inplace=True)

        # Lists of indices from best/worst slices we want to add to dataSlice
        b_index_list = [
            f"Previous Best {column.column_name}" for column in columns[1:]
        ]
        w_index_list = [
            f"Previous Worst {column.column_name}" for column in columns[1:]
        ]

        # Define return_slice
        return_slice = pd.concat(
            [data_slice, best_slice.loc[b_index_list], worst_slice.loc[w_index_list]],
            axis=0,
        )

        return return_slice

    """ METHODS """
    # Method that loops through a slice of possible best hits, finding the best
    # one using the given constraints
    def _constrain_loop(
            self,
            const_df: pd.DataFrame,
            RT_i: int | float,
            test_slice: pd.DataFrame,
            prior_list: list[int | float],
            in_columns: list[_ColumnID],
            out_columns: list[_ColumnID]
            ):
        """
        Method that loops through a slice of possible best hits, finding the best
        one using the given constraints.

        Parameters
        ----------
        const_df : pandas.DataFrame
            The DataFrame containing best hits by retention time,
            with each row being the result of selection by this looping filter.
        RT_i : int | float
            The retention time of the test_slice.
        test_slice : pandas.DataFrame
            The slice containing all compounds assigned to RT_i.
        prior_list : list[int | float]
            A list of unique priorities across all soft_bar elements.
        in_columns : list[_ColumnID]
            A list of columns defining the test_slice.
        out_columns : list[_ColumnID]
            A list of columns to export to const_df.

        Returns
        -------
        _type_
            _description_
        """

        # Get the passed columns
        rt_column, compound_column, formula_column, ranking_column = in_columns

        # Find rows with best and worst rankings
        best_match = test_slice.iloc[0, :]
        worst_match = test_slice.iloc[-1, :]

        # Set counted_loops to 0
        counted_loops = 0

        # While loop to continue search function until match is either found
        # or not. Checks if counted_loops is greater than the length of priorities list
        while counted_loops <= len(prior_list) + 1:

            # For every row in the slice sorted by match factor..
            for index, row in test_slice.iterrows():

                # If the formula meets the no_bar criteria, choose row and return
                if self._filter_no_bar(
                   row[formula_column.column_name]
                   ) and counted_loops == 0:

                    # Create a Series to append
                    const_series = self._concat_series(
                        row,
                        best_match,
                        worst_match,
                        in_columns
                        )

                    # Add the row to the DataFrame
                    const_df = self._concat_df(const_series, const_df, out_columns)

                    return const_df

                # Otherwise if the formula meets the soft_bar criteria and the number
                # of counted_loops is greater than zero
                elif counted_loops > 0 \
                    and counted_loops <= len(prior_list) \
                    and self._filter_soft_bar(
                        row[formula_column.column_name],
                        prior_list[counted_loops - 1]
                        ):

                    # Create a Series to append
                    const_series = self._concat_series(
                        row,
                        best_match,
                        worst_match,
                        in_columns
                        )

                    # Add the row to the DataFrame
                    const_df = self._concat_df(const_series, const_df, out_columns)

                    return const_df

                # Otherwise if the loop number is greater than the number of
                # listed priorities, add row with "No Match" and formula NaN
                elif counted_loops > len(prior_list):

                    # Create a Series to append
                    const_series = self._concat_series(
                        pd.Series(
                            {
                                rt_column.column_name: RT_i,
                                compound_column.column_name: "No Match",
                                formula_column.column_name: float("nan"),
                                ranking_column.column_name: float("nan")
                            }
                        ),
                        best_match,
                        worst_match,
                        in_columns
                        )

                    # Add the row to the DataFrame
                    const_df = self._concat_df(const_series, const_df, out_columns)

                    return const_df

            # Count one while loop
            counted_loops += 1

        return const_df

    # Method to return True if formula only contains no_bar restrictions
    def _filter_no_bar(
            self,
            formula: str,
            ):
        """
        Method to return True if formula only contains no_bar restrictions

        Parameters
        ----------
        formula : str
            Chemical formula to analyze.

        Returns
        -------
        tf: bool
            True if formula only contains no_bar elements, False otherwise.

        """

        # Try...
        try:
            # Find all Elements present in formula
            elements = re.findall("[A-Z][a-z]?", formula)
            # Get list of allowed Elements from no_bar dataframe
            allowed_elements = [self.no_bar[i].symbol for i in range(len(self.no_bar))]

            # If a set of the difference between the lists is not empty (there are
            # formula Elements besides allowed ones), return False
            if set(elements).difference(set(allowed_elements)):
                tf = False
            # Otherwise, return True
            else:
                tf = True

        # If TypeError, return False
        except TypeError:
            tf = False

        return tf

    # Method to return True if formula only contains soft_bar restrictions of
    # given priority or greater
    def _filter_soft_bar(
            self,
            formula: str,
            priority: int
            ):

        # Try...
        try:
            # Find all Elements present in formula
            formula_elements = re.findall("[A-Z][a-z]?", formula)
            # Get dataframe of Elements and priority from soft_bar
            elements_df = pd.DataFrame.from_dict(
                {
                    "Symbol": [obj.symbol for obj in self.soft_bar],
                    "Priority": [obj.priority for obj in self.soft_bar],
                }
            )
            # Get list of symbols with provided priority or greater, add Elements from
            # no_bar
            allowed_elements = elements_df.loc[
                elements_df["Priority"] >= priority, "Symbol"
                ].to_list()
            allowed_elements.extend(
                [self.no_bar[i].symbol for i in range(len(self.no_bar))]
            )
            # If a set of the difference between the lists is not empty (there are
            # formula Elements besides allowed ones), return False
            if set(formula_elements).difference(set(allowed_elements)):
                tf = False
            # Otherwise, return True
            else:
                tf = True

        # If TypeError, return False
        except TypeError:
            tf = False

        return tf

    # Method to group retention times, taking median to be value of grouped peaks
    def _group_rt(
            self,
            raw_df: pd.DataFrame,
            rt_column_name: str
            ):
        """

        Parameters
        ----------
        raw_df : pandas.DataFrame
            DataFrame containing all possible hits, including hits of identical
            retention time.
        rt_column_name: str
            Name of the column containing retention times.

        Returns
        -------
        filter_df: pandas.DataFrame
            DataFrame containing all possible hits each assigned a median retention
            time of their group.

        """

        # Redefine for clarity
        filter_df = raw_df.copy()

        # Set up empty list for output RT (rt_permF), an empty list for temporary
        # (original) RT's (rt_temp) with only the first original RT, and the
        # median of that list
        rt_permF = []
        rt_temp = [raw_df[rt_column_name][0]]
        rt_temp_median = rt_temp[0]

        # For all raw retention times, group times within the PeakRTLim of each
        # other.
        for i in range(1, len(raw_df[rt_column_name])):
            # Current retention time
            rt_current = raw_df[rt_column_name][i]

            # If current retention time within the median plus the peak limits,
            # redefine median
            if (
                rt_current < rt_temp_median + self.peak_rt_error
                and rt_current > rt_temp_median - self.peak_rt_error
            ):

                # Append to list of like retention times
                rt_temp.append(rt_current)
                # Recalculate median, rounding to 4 decimal places
                rt_temp_median = round(np.median(rt_temp), 4)
                # If it's reached the end of the dataframe, append what's left
                if i == len(raw_df[rt_column_name]) - 1:
                    rt_permF.extend(np.full(len(rt_temp), rt_temp_median))
                    rt_temp_median = rt_current
                    rt_temp = [rt_current]

            # Otherwise, save the rt_temp_median to all rt_temp positions,
            # redefine rt_temp and rt_temp_median
            else:
                # Set old retention times to median
                filter_df.loc[i - len(rt_temp) : i, (rt_column_name)] = rt_temp_median
                rt_permF.extend(np.full(len(rt_temp), rt_temp_median))
                rt_temp_median = rt_current
                rt_temp = [rt_current]

        return filter_df

    # Method to choose best matches according to compound constraints
    def constrain(
            self,
            table: Table,
            rt_column: _ColumnID,
            compound_column: _ColumnID,
            formula_column: _ColumnID,
            ranking_column: _ColumnID
            ):
        """
        This method loops through the dataframe, selecting the best match out of
        duplicate retention time matches. The process in this method is as follows:

        1) Get a list of all retention times in the dataframe;
        2) Loop through each retention time, getting a slice of each dataframe;
        3) Loop through compound constraints to pick the best match in the slice;
        4) Append result to new, constrained dataframe

        For selecting the best match:

        1) If first formula of sorted slice contains only no_bar, add to constrained
           dataframe. Otherwise, repeat test until entire slice is passed.
        3) If all other formulas have Elements besides no_bar, go back to first value
           and allow its formula if it contains only highest priority Elements
        4) If it contains lower priority/blocklist Elements, repeat down slice
        5) If all formulas contain lower priority Elements, allow the next priority and
           repeat search
        5) If all formulas contain Elements not listed in no_bar or soft_bar, add
           "No Match" row

        Parameters
        ----------
        table : Table
            The Table to be filtered

        rt_column: _ColumnID
            The ColumnID corresponding to the Table column containing retention times.

        compound_column: _ColumnID
            The ColumnID corresponding to the Table column containing compound names.

        formula_column: _ColumnID
            The ColumnID corresponding to the Table column containing compound formulas.

        ranking_column: _ColumnID
            The ColumnID corresponding to the Table column containing hit rankings.
            'Rankings' here refers to any measure of compound hit accuracy (e.g.,
            'Match Factor').

        Returns
        -------
        None

        """

        # Get the Pandas DataFrame contained in the Table
        raw_df = table.data.copy()

        # Group the compounds by retention time
        filter_df = self._group_rt(raw_df, rt_column.column_name)

        # Get list of written priorities from soft_bar and sort them by descending
        prior_list = sorted(
            list(set([x.priority for x in self.soft_bar])),
            reverse=True
            )

        # Get list of all retention times
        arrayRF = filter_df[rt_column.column_name].unique()

        # Create a list of new columns
        # If showing previous matches...
        if self.do_show_previous_matches:
            # Include previous matches in the list
            columns = [
                rt_column.column_name,
                compound_column.column_name,
                formula_column.column_name,
                ranking_column.column_name,
                f"Previous Best {compound_column.column_name}",
                f"Previous Best {formula_column.column_name}",
                f"Previous Best {ranking_column.column_name}",
                f"Previous Worst {compound_column.column_name}",
                f"Previous Worst {formula_column.column_name}",
                f"Previous Worst {ranking_column.column_name}"
                ]
        # Otherwise...
        else:
            # Only include filtered matches
            columns = [
                rt_column.column_name,
                compound_column.column_name,
                formula_column.column_name,
                ranking_column.column_name
                ]

        # Create dictionary for output data
        const_df = pd.DataFrame(columns=columns)

        # For every listed retention time, select best match
        for RT_i in arrayRF:

            # Get a slice containing all possible compounds at given RT
            compound_slice = filter_df.loc[(filter_df[rt_column.column_name] == RT_i)]

            # Sort slice by ranking, reset indices
            test_slice = compound_slice.sort_values(
                by=[ranking_column.column_name], ascending=False
                ).reset_index(drop=True)

            # Apply constraints
            const_df = self._constrain_loop(
                const_df,
                RT_i,
                test_slice,
                prior_list,
                [rt_column, compound_column, formula_column, ranking_column],
                columns
            )

        # Set the Table's data attribute to the newly constrained DataFrame
        table.data = const_df.sort_values(
            by=rt_column.column_name,
            ascending=True,
            ignore_index=True
            )

        return None
