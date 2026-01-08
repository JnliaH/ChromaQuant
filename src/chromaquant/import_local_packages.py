"""
COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

FUNCTIONS FOR IMPORTING LOCAL PACKAGES

Julia Hancock
Started 1-7-2026

"""

import os
import importlib.util
import sys


# Function to get a dictionary of subpackage directories
def get_local_package_directories():

    # Get package directory
    app_dir = os.path.dirname(os.path.abspath(__file__))

    # Get absolute directories for subpackages
    subpack_dir = {'Handle': os.path.join(app_dir, 'Handle', '__init__.py'),
                   'Match': os.path.join(app_dir, 'Match', '__init__.py'),
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
