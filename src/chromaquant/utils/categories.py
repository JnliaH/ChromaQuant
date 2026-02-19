#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The Categories class is used to define categories by which DataSets (in
particular, Tables) can be categorized. Users add categories as dictionaries
where the key is a string describing the category and the value is a list of
values that should be assigned the category. The user selects a categorizer
(either IS_EQUAL or IS_IN) to determine whether values should be exact matches
to category values or whether they can have category values as substrings.

"""

""" CLASS """


# Define categories class
class Categories:
    """
    Class that is used to define categories by which Tables can be
    categorized.

    Raises
    ------
    AttributeError
        If the IS_IN method is used for non-string values or keywords.

    """
    # Initialize
    def __init__(self):

        # Create attributes
        # Category attribute
        # Expected format is:
        #   {'category 1': ['keyword 1', 'keyword 2', ...], ...}
        self._categories = {}

        # Categorizer attribute
        self.categorizer = self.IS_EQUAL

        # Attribute denoting whether to ignore string case
        self.ignore_case = True

    # Define get_item to get internal categories
    def __getitem__(self, key):
        # Get category
        return self._categories[key]

    # Define set_item to set internal categories
    def __setitem__(self, key, value):
        # Set category
        self._categories[key] = value

    """ METHODS """
    # Method to categorize by finding when tested value is equal to keyword,
    # selecting first applicable category if more than one apply
    def IS_EQUAL(self, test_value: str | int | float) -> str:
        """
        A categorizer that finds when a tested value is equal to a keyword.

        Parameters
        ----------
        test_value : str | int | float
            Value to categorize.

        Returns
        -------
        category : str
            The applicable category for the test_value.

        """

        # For every category in categories...
        for category in self._categories:

            # For every keyword in the category...
            for keyword in self._categories[category]:

                # If the keyword is equal to the test value...
                if keyword == test_value:

                    # Return the category
                    return category

                # Otherwise, pass
                else:
                    pass

        return ''

    # Method to categorize by finding when keyword is a substring of a tested
    # value, selecting first applicable category if more than one apply
    def IS_IN(self, test_value: str) -> str:

        # Try to get the lowercase of the test_value and all keywords
        try:
            test_value.lower()
            test_keyword_list = [keyword.lower() for keyword_list in
                                 list(self._categories.values()) for
                                 keyword in keyword_list]
            del test_keyword_list

        # Raise error if AttributeError occurs
        except AttributeError as e:
            raise AttributeError(('Cannot use IS_IN for non-string'
                                  f'values and keywords: {e}'))

        # For every category in categories...
        for category in self._categories:

            # For every keyword in the category...
            for keyword in self._categories[category]:

                # If ignoring case...
                if self.ignore_case is True:

                    # If the lowercase keyword is in
                    # the lowercase test value...
                    if keyword.lower() in test_value.lower():

                        # Return the category
                        return category

                    # Otherwise, pass
                    else:
                        pass

                # If not ignoring case...
                else:

                    # If the keyword is in the test value...
                    if keyword in test_value:

                        # Return the category
                        return category

                    # Otherwise, pass
                    else:
                        pass

        return ''
