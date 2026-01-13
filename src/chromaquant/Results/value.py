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

CLASS DEFINITION FOR VALUES

Julia Hancock
Started 01-12-2025

"""

from .dataset import DataSet
from .. import logging_and_handling as lah


""" LOGGING AND HANDLING """

# Get the logger
logger = lah.setup_logger()

# Get an error logging decorator
error_logging = lah.setup_error_logging(logger)

""" CLASS """


class Value(DataSet):

    def __init__(self, data, *args, **kwargs):

        # Run DataSet initialization
        super().__init__(*args, **kwargs)

        # Initialize data variable
        self.data = data
