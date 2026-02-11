#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The Import Local Packages module is used internally to import subpackages into
the main package and other subpackages. It will be deprecated in future
versions.

"""

import os
import importlib.util
import sys


# Function to get a dictionary of subpackage directories
def get_local_package_directories():

    # Get package directory
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # Get absolute directories for subpackages
    subpack_dir = {'utils': os.path.join(app_dir, 'utils', '__init__.py'),
                   'Signal': os.path.join(app_dir, 'Signal', '__init__.py'),
                   'Results': os.path.join(app_dir, 'Results', '__init__.py')}

    return subpack_dir


# Define function to import from path
def import_from_path(module_name, path):

    # Define spec
    spec = importlib.util.spec_from_file_location(module_name, path)

    # Define module
    module = importlib.util.module_from_spec(spec)

    # Expand sys.modules dict
    sys.modules[module_name] = module

    # Load module
    spec.loader.exec_module(module)

    return module
