#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Copyright (c) 2026, by Julia Hancock
License: BSD 3-Clause License

UNIT TESTING FOR THEME

"""

import chromaquant as cq

""" TEST CLASS """


class TestTheme:

    # Test theme creation and default style import
    def test_theme_import(self):

        # Create a new theme
        new_theme = cq.Theme()

        assert new_theme.header._alignment['horizontal'] == 'center'
