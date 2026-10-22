"""

HitFilter is used to apply a basic, chemical-element-based filter to a Table containing
compound best hits sorted by retention time.

"""

import re

import numpy as np
import pandas as pd

from ..data.table import Table
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
    def _concat_df(data_slice: pd.Series, df_in: pd.DataFrame):
        """
        Method that adds best hit match data to the best hit DataFrame

        Parameters
        ----------
        data_slice : pandas.Series
            Series containing best hit match data for one retention time.
        df_in : pandas.DataFrame
            DataFrame containing prior best hit match data or no match data.

        Returns
        -------
        df_out: pandas.DataFrame
            DataFrame containing prior and current best hit match data.

        """

        # Assumes a dataframe provided with these columns:
        # ['Component RT', 'Compound Name', 'Formula', 'Match Factor']
        # Also assumes dataSlice will contain at least these same columns
        col = [
            "Component RT",
            "Compound Name",
            "Formula",
            "Match Factor",
            "Previous Best Compound Name",
            "Previous Best Formula",
            "Previous Best Match Factor",
            "Previous Worst Compound Name",
            "Previous Worst Formula",
            "Previous Worst Match Factor",
        ]

        # Get a list of data slice values
        list_out = [data_slice[col[i]] for i in range(len(col))]

        # Make a data slice dataframe and reindex it
        data_slice_df = pd.DataFrame([list_out], columns=col)

        # Get the output dataframe
        df_out = pd.concat(
            [data_slice_df.astype(object), df_in.astype(object)], ignore_index=True
        )

        return df_out

    # Method to add series of matches with best and worst match factor to a
    # selected match series
    @staticmethod
    def _concat_series(
        data_slice: pd.Series, best_slice: pd.Series, worst_slice: pd.Series
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

        Returns
        -------
        return_slice: pd.Series
            Series containing best, previous best, and previous worst hits for a given
            retention time.

        """
        # Assumes all Series have these columns:
        # ['Component RT','Compound Name','Formula','Match Factor']

        # Define dictionaries of new index names for bestSlice and worstSlice
        b_index = {
            "Component RT": "Previous Best Component RT",
            "Compound Name": "Previous Best Compound Name",
            "Formula": "Previous Best Formula",
            "Match Factor": "Previous Best Match Factor",
        }
        w_index = {
            "Component RT": "Previous Worst Component RT",
            "Compound Name": "Previous Worst Compound Name",
            "Formula": "Previous Worst Formula",
            "Match Factor": "Previous Worst Match Factor",
        }

        # Rename bestSlice and worstSlice indices
        best_slice = best_slice.copy()
        worst_slice = worst_slice.copy()
        best_slice.rename(index=b_index, inplace=True)
        worst_slice.rename(index=w_index, inplace=True)

        # Lists of indices from best/worst slices we want to add to dataSlice
        b_index_list = [
            "Previous Best Compound Name",
            "Previous Best Formula",
            "Previous Best Match Factor",
        ]
        w_index_list = [
            "Previous Worst Compound Name",
            "Previous Worst Formula",
            "Previous Worst Match Factor",
        ]

        # Define return_slice
        return_slice = pd.concat(
            [data_slice, best_slice.loc[b_index_list], worst_slice.loc[w_index_list]],
            axis=0,
        )

        return return_slice

    """ METHODS """

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

        return tf

    # Method to return True if formula only contains soft_bar restrictions of
    # given priority
    def _filter_soft_bar(self, formula: str, priority: int):

        # Find all Elements present in formula
        Elements = re.findall("[A-Z][a-z]?", formula)
        # Get dataframe of Elements and priority from soft_bar
        ePDF = pd.DataFrame.from_dict(
            {
                "Symbol": [obj.symbol for obj in self.soft_bar],
                "Priority": [obj.priority for obj in self.soft_bar],
            }
        )
        # Get list of symbols with provided priority or lower, add Elements from
        # no_bar
        allowed_Elements = ePDF.loc[ePDF["Priority"] <= priority, "Symbol"].to_list()
        allowed_Elements.extend(
            [self.no_bar[i].symbol for i in range(len(self.no_bar))]
        )

        # If a set of the difference between the lists is not empty (there are
        # formula Elements besides allowed ones), return False
        if set(Elements).difference(set(allowed_Elements)):
            tf = False
        # Otherwise, return True
        else:
            tf = True

        return tf

    # Method to group retention times, taking median to be value of grouped peaks
    def _group_rt(self, raw_df: pd.DataFrame):
        """

        Parameters
        ----------
        raw_df : pandas.DataFrame
            DataFrame containing all possible hits, including hits of identical
            retention time.

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
        rt_temp = [raw_df["Component RT"][0]]
        rt_temp_median = rt_temp[0]

        # For all raw retention times, group times within the PeakRTLim of each
        # other.
        for i in range(1, len(raw_df["Component RT"])):
            # Current retention time
            rt_current = raw_df["Component RT"][i]

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
                if i == len(raw_df["Component RT"]) - 1:
                    rt_permF.extend(np.full(len(rt_temp), rt_temp_median))
                    rt_temp_median = rt_current
                    rt_temp = [rt_current]

            # Otherwise, save the rt_temp_median to all rt_temp positions,
            # redefine rt_temp and rt_temp_median
            else:
                # Set old retention times to median
                filter_df.loc[i - len(rt_temp) : i, ("Component RT")] = rt_temp_median
                rt_permF.extend(np.full(len(rt_temp), rt_temp_median))
                rt_temp_median = rt_current
                rt_temp = [rt_current]

        return filter_df

    # Method to choose best matches according to compound constraints
    def constrain(
            self,
            table: Table
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
           dataframe
        2) Otherwise, test next formula
        3) If all other formulas have Elements besides no_bar, go back to first value
           and allow its formula if it contains only highest priority Elements
        4) If it contains lower priority/blocklist Elements, repeat down slice
        5) If all formulas contain lower priority Elements, allow the next priority and
           repeat search
        5) If all formulas contain Elements not listed in no_bar or soft_bar, add
           "No Match" row

        Parameters
        ----------
        table : table
            The Table to be filtered

        Returns
        -------
        None

        """

        # Get the Pandas DataFrame contained in the Table
        raw_df = table.data.copy()
        # Group the compounds by retention time
        filter_df = self._group_rt(raw_df)
        # Get list of written priorities from soft_bar and sort them by descending
        priorList = sorted(list(set([x.Priority for x in self.soft_bar])))
        # Get list of all retention times
        arrayRF = filter_df["Component RT"].unique()
        # Create dictionary for outputted data
        constDF = pd.DataFrame(
            columns=[
                "Component RT",
                "Compound Name",
                "Formula",
                "Match Factor",
                "Previous Best Compound Name",
                "Previous Best Formula",
                "Previous Best Match Factor",
                "Previous Worst Compound Name",
                "Previous Worst Formula",
                "Previous Worst Match Factor",
            ]
        )

        # For every listed retention time, select best match
        for RTi in arrayRF:

            # Get a slice containing all possible compounds at given RT
            compound_slice = filter_df.loc[(filter_df["Component RT"] == RTi)]
            # Remove Unknowns from slice, if slice is empty then skip one loop
            compound_slice = compound_slice.loc[
                ~compound_slice["Compound Name"].str.contains("Unknown")
            ]
            # Sort slice by match factor, reset indices
            test_slice = compound_slice.sort_values(
                by=["Match Factor"], ascending=False
            ).reset_index(drop=True)

            # Find rows with best and worst match factors
            try:
                best_match = test_slice.iloc[0, :]
                worst_match = test_slice.iloc[len(test_slice) - 1, :]

            except Exception:
                best_match = pd.Series(
                    dtype="float64",
                    index=["Component RT", "Compound Name", "Formula", "Match Factor"],
                )
                worst_match = pd.Series(
                    dtype="float64",
                    index=["Component RT", "Compound Name", "Formula", "Match Factor"],
                )

            # Set search True/False Boolean to True
            search_tf = True
            # Set counted_loops to 0
            counted_loops = 0
            # While loop to continue search function until match is either found
            # or not
            while search_tf is True and counted_loops < 100:

                # For every row in the slice sorted by match factor..
                for index, row in test_slice.iterrows():
                    # If the formula meets the no_bar criteria, choose row and
                    # break formula
                    if self._filter_no_bar(row["Formula"]) and counted_loops == 0:
                        constSeries = self._concat_series(row, best_match, worst_match)
                        constDF = self.concat_DF(constSeries, constDF)
                        search_tf = False
                        break
                    # Otherwise if the loop number is greater than 0 and less than
                    # the number of unique soft_bar priorities, determine if
                    # formula meets soft_bar criteria
                    elif counted_loops > 0 and counted_loops < len(priorList):
                        # Try/except in case the counted loops goes higher than the
                        # priority list
                        try:
                            if self._filter_soft_bar(
                                row["Formula"], priorList[counted_loops - 1]
                            ):
                                constSeries = self._concat_series(
                                    row, best_match, worst_match
                                )
                                constDF = self._concat_df(constSeries, constDF)
                                search_tf = False
                                break
                            else:
                                pass
                        except Exception:
                            pass
                    # Otherwise if the loop number is greater than the number of
                    # listed priorities, add row with "No Match" and formula NaN
                    elif counted_loops > len(priorList):
                        constSeries = self._concat_series(
                            pd.Series(
                                {
                                    "Component RT": RTi,
                                    "Compound Name": "No Match",
                                    "Match Factor": float("nan"),
                                    "Formula": float("nan"),
                                }
                            ),
                            best_match,
                            worst_match,
                        )
                        constDF = self._concat_df(constSeries, constDF)
                        search_tf = False
                        break
                    else:
                        pass

                # Count one while loop
                counted_loops += 1

        # Set the Table's data attribute to the newly-constrained DataFrame
        table.data = constDF

        return None
