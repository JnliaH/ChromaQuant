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

SCRIPT FOR PERFORMING QUANTIFICATION STEPS

Julia Hancock
Started 12-29-2024

"""

""" PACKAGES """
import sys
import pandas as pd
import os
from molmass import Formula
import math
import numpy as np
from chemformula import ChemFormula
import json
from datetime import datetime
import logging
import importlib.util

""" LOCAL PACKAGES """

#Get package directory
app_dir =  os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#Get absolute directories for subpackages
subpack_dir = {'Handle':os.path.join(app_dir,'Handle','__init__.py'),
               'Manual':os.path.join(app_dir,'Manual','__init__.py'),
               'QuantSub':os.path.join(app_dir,'Quant/QuantSub','__init__.py')}

#Define function to import from path
def import_from_path(module_name,path):
    #Define spec
    spec = importlib.util.spec_from_file_location(module_name,path)
    #Define modules
    module = importlib.util.module_from_spec(spec)
    #Expand sys.modules dict
    sys.modules[module_name] = module
    #Load module
    spec.loader.exec_module(module)
    return module

#Import all local packages
hd = import_from_path("hd",subpack_dir['Handle'])
mn = import_from_path("mn",subpack_dir['Manual'])
qtsb = import_from_path("qt",subpack_dir['QuantSub'])

""" VARIABLES FOR TESTING """
sname = 'example2'
quantphases = 'LG'

""" DIRECTORIES """
print("[quantMain] Getting directories...")
#Get directories from handling script
directories = hd.handle(app_dir)

#Data file log directory
directories['log'] = os.path.join(directories['data'],sname,'log')

#Data file breakdowns directory
directories['break'] = os.path.join(directories['data'],sname,'breakdowns')

#Raw data file directory
directories['raw'] = os.path.join(directories['data'],sname,'raw data')

""" ANALYSIS CONFIGURATION """
print("[quantMain] Interpreting analysis configuration...")
#Read analysis configuration file
with open(os.path.join(directories['resources'],'analysis-config.json')) as f:
    analysis_config = json.load(f)

#Extract analysis configuration info
#This dictionary contain lists of substrings to be checked against compound name strings to
#assign a compound type

#Six compound types exist: linear alkanes (L), branched alkanes (B), aromatics (A), cycloalkanes (C),
#alkenes/alkynes (E), and other (O)

#Each compound type abbreviation will have an entry in the dictionary corresponding to a list of
#substrings to be checked against a compound name string

#File suffixes to add to form data filenames
file_suffix = analysis_config['file-suffix']

#Acceptable peak errors for matching
peak_errors = analysis_config['peak-errors']

#Dictionary of compound lumps
CL_Dict = analysis_config['CL_Dict']

#Dictionary of compound types
CT_Dict = analysis_config['CT_Dict']

""" EVALUATING PARAMETERS """
print("[quantMain] Evaluating run parameters...")

#Define liquid-gas Boolean for running analysis
lgTF = qtsb.evalRunParam(quantphases)

#If liquid-gas Boolean is None, terminate quantification
if lgTF == None:
    print("[quantMain] No phases selected, terminating script")
    #Terminate script
    sys.exit()

#Define peak error using analysis-config
peak_error = peak_errors['peak-error-third']

#Define boolean describing whether or not an external standard was used for gas analysis
ES_bool = True

#Define temperature and pressure of gas bag used in sample injection
gasBag_temp = analysis_config['sample-injection-conditions']['gas-bag-temp-C']               #C
gasBag_pressure = analysis_config['sample-injection-conditions']['gas-bag-pressure-psia']    #psi

""" RESPONSE FACTOR INFO """
print("[quantMain] Searching for response factors...")
#Liquid response factor file name
LRF_path = qtsb.findRecentFile('LRF','.xlsx',directories['rf'])
#FID gas response factor file name
FIDRF_path = qtsb.findRecentFile('FIDRF','.csv',directories['rf'])
#TCD gas response factor file name
TCDRF_path = qtsb.findRecentFile('TCDRF','.csv',directories['rf'])

print(LRF_path,FIDRF_path,TCDRF_path)