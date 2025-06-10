#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2024, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
	      URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SCRIPT FOR HANDLING FILE DIRECTORIES

Julia Hancock
7-29-2024
"""

""" PACKAGES """
import json
import os
import getpass

""" FUNCTIONS """

def handle(props):
    #fileDir is the passed absolute directory of the currently running file

    #Define app directory
    D_app = props['app-directory']

    #Define file directory
    D_files = props['file-directory']
    
    #Define resources directory
    D_rsc = os.path.join(D_files,'resources')
    
    #Define theme directory
    D_theme = os.path.join(D_rsc,'forest','forest-light.tcl')
    
    #Define response factors directory
    D_rf = os.path.join(D_files,'response-factors')
    
    #Define data directory
    D_data = os.path.join(D_files,'data')
    
    #Define images directory
    D_img = os.path.join(D_files,'images')
    
    #Return directories as a dictionary
    return {'app':D_app,'files':D_files,'resources':D_rsc,'theme':D_theme,'rf':D_rf,'data':D_data,'images':D_img}