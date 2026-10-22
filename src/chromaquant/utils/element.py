"""

Element is used to define chemical element filters for HitFilter

"""


class Element:
    """
    Class used to define a chemical Element and its priority in hit filtering.
    """

    def __init__(self, symbol: str, priority: int = 1):

        # Set symbol attribute
        self.symbol = symbol

        # Set priority
        self._priority = priority
