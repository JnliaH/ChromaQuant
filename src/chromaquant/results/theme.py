#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This submodule contains the Theme class definition.

"""

import logging
import json
from openpyxl.styles import PatternFill, Border, Side, \
                            Alignment, Protection, Font
import os
from ..logging_and_handling import setup_logger, setup_error_logging

""" LOGGING AND HANDLING """

# Create a logger
logger = logging.getLogger(__name__)

# Format the logger
logger = setup_logger(logger)

# Get an error logging decorator
error_logging = setup_error_logging(logger)


""" STYLEGROUP CLASS"""


# Define StyleProperty class
class StyleProperty:

    # Descriptor __set_name__
    def __set_name__(self, owner, name):
        self.name = '_' + name

    # Getter
    def __get__(self, obj, type=None):
        return getattr(obj, self.name)

    # Setter
    def __set__(self, obj, value):
        setattr(obj, self.name, value)


# Define the StyleGroup class
class StyleGroup:
    """
    StyleGroup objects contain details about how to format each
    cell style.
    """

    # Create class instances of StyleProperty for every property
    font = StyleProperty()
    fill = StyleProperty()
    border = StyleProperty()
    alignment = StyleProperty()
    protection = StyleProperty()
    number_format = StyleProperty()

    # Initialize method
    def __init__(self):

        # Define dictionaries for style category defaults
        # Default Font values
        self.font = {'font': 'Calibri',
                     'size': 11,
                     'bold': False,
                     'italic': False,
                     'vertAlign': None,
                     'underline': None,
                     'strike': False,
                     'color': '000000'}
        # Default PatternFill values
        self.fill = {'fill_type': None,
                     'start_color': 'FFFFFF',
                     'end_color': 'FFFFFF'}
        # Default Border values
        self.border = {'left': Side(border_style=None, color='000000'),
                       'right': Side(border_style=None, color='000000'),
                       'top': Side(border_style=None, color='000000'),
                       'bottom': Side(border_style=None, color='000000'),
                       'diagonal': Side(border_style=None, color='000000'),
                       'diagonal_direction': 0,
                       'outline': Side(border_style=None, color='000000'),
                       'vertical': Side(border_style=None, color='000000'),
                       'horizontal': Side(border_style=None, color='000000')
                       }
        # Default Alignment values
        self.alignment = {'horizontal': 'general',
                          'vertical': 'bottom',
                          'text_rotation': 0,
                          'wrap_text': False,
                          'shrink_to_fit': False,
                          'indent': 0}
        # Default Protection values
        self.protection = {'locked': False,
                           'hidden': False}
        # Default Number format
        self.number_format = 'General'


""" THEME CLASS """


# Define the Theme class
class Theme:
    """
    Theme objects contain details about how to format reports from
    exporting Results.
    """

    # Initialize method
    def __init__(self):

        # Create style groups
        self.header = StyleGroup()
        self.subheader = StyleGroup()
        self.body = StyleGroup()

        # Get the current script path
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Load the default cqtheme
        self.import_theme(
            os.path.join(script_dir, 'themes', 'default.cqtheme')
            )

    # Method to import theme from .cqtheme
    def import_theme(self, path):

        # Load the .cqtheme at path
        with open(path, 'r') as f:
            theme_dict = json.load(f)

        # Unpack the default style properties
        for group, group_dict in theme_dict.items():
            for category, category_val in group_dict.items():
                setattr(getattr(self, group), category, category_val)

        return None
