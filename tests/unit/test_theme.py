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

UNIT TESTING FOR THEME

Julia Hancock
Started 6-16-2026

"""

import chromaquant as cq

""" TEST CLASS """


class TestTheme:

    # Test theme creation and default style import
    def test_theme_import(self):

        # Create a new theme
        new_theme = cq.Theme()

        assert new_theme.header.alignment['horizontal'] == 'center'
