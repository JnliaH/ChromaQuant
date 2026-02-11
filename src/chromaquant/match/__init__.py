#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This module provides a function for matching two Pandas DataFrames (match)
and a class for defining the parameters by which to match (MatchConfig).

"""

from .match_config import MatchConfig
from .match_tools import match_dataframes
from .match import match
