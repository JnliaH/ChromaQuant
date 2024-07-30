#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT FOR HANDLING FILE DIRECTORIES

Julia Hancock
7-29-2024
"""

""" PACKAGES """
import json
import os

""" FUNCTIONS """

def handle(fileDir):
    #fileDir is the passed absolute directory of the currently running file
    
    #Import sample information from json file
    with open(os.path.join(fileDir,'properties.json')) as props_f:
        props = json.load(props_f)
        
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
    return {'files':D_files,'resources':D_rsc,'theme':D_theme,'rf':D_rf,'data':D_data,'images':D_img}