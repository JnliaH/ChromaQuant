# -- Change project source directory -----------------------------------------

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))


# -- Project information -----------------------------------------------------

project = 'ChromaQuant'
copyright = '2026, Julia Hancock'
author = 'Julia Hancock'
release = '0.5.0'


# -- General configuration ---------------------------------------------------

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.autosummary',
              'sphinx_rtd_theme']
autosummary_generate = False
autodoc_default_options = {'members': True,
                           'undoc-members': False}
templates_path = ['_templates']
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_options = {"navigation_depth": 3,
                      "collapse_navigation": False}
html_static_path = ['../source/_static']


# -- Custom CSS --------------------------------------------------------------
def setup(app):
    app.add_css_file('chromaquant.css')
