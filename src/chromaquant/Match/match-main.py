"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2024, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
	      URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SCRIPT THAT MATCHES FID AND MS PEAKS

Julia Hancock
Started 12/10/2023

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
import scipy
import importlib.util

""" DIRECTORIES (MANUAL) """
testPath = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/chromaquant/src/chromaquant/"
#Define file directory
D_files = "/Users/connards/Documents/ChromaQuant"

#Define app directory
D_app = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/chromaquant/src/chromaquant"
    
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

directories = {'files':D_files,'resources':D_rsc,'theme':D_theme,'rf':D_rf,'data':D_data,'images':D_img}

""" VARIABLES FOR TESTING"""

sname = 'example2'
sphase = 'L'

""" LOCAL PACKAGES """

#Get absolute directories for subpackages
subpack_dir = {'Handle':os.path.join(D_app,'Handle','__init__.py'),
               'Manual':os.path.join(D_app,'Manual','__init__.py'),
               'MatchSub':os.path.join(D_app,'Match/MatchSub','__init__.py')}

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
mtsb = import_from_path("mtsb",subpack_dir['MatchSub'])

""" DIRECTORIES """

#Data file log directory
directories['log'] = os.path.join(directories['data'],sname,'log')

#Data file breakdowns directory
directories['break'] = os.path.join(directories['data'],sname,'breakdowns')

#Raw data file directory
directories['raw'] = os.path.join(directories['data'],sname,'raw data')

""" ANALYSIS CONFIGURATION """

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

contains = analysis_config["CT-assign-contains"]

#Tuple of contains keys in order of priority
keyloop = analysis_config["CT-assign-keyloop"]

#Tuple of elements to be excluded and automatically labelled as 'O'
element_exclude = analysis_config["CT-assign-element-exclude"]

#File suffixes to add to form data filenames
file_suffix = analysis_config["file-suffix"]

#Fit paramters for matching gas FID and gas MS
gas_match_fit_parameters = analysis_config["gas-match-fit-parameters"]

#Acceptable peak errors for matching
peak_errors = analysis_config["peak-errors"]

""" RUN FUNCTIONS """

#Run the file naming function – this function will create paths to all relevant files for matching FID and MS peaks according to sample name and phase
paths = hd.fileNamer(sname,sphase,file_suffix,directories['raw'])

# Run the file checking function – this function will search for an existing FIDpMS file, creating one if it does not exist. 
# It will then read the file as a pandas DataFrame. The tf Boolean describes whether or not there exist manually-matched peaks.
fpmDF, tf = hd.checkFile(paths[2],paths[0])

# Import MS UPP data
mDF = pd.read_csv(paths[1])

# Get only relevant columns of MS UPP data
mDF = mDF.loc[:,['Component RT','Compound Name','Formula','Match Factor']]

# Third order function for testing
fit = lambda FID_RT: 0.0252*FID_RT**3 - 0.5274*FID_RT**2 + 4.8067*FID_RT - 3.0243

# Run the matching function – this function takes a passed function describing an estimated relationship between MS RT's and FID RT's and matches peaks. 
# Function can be of any form as long as it returns a floating point value for the estimated MS RT
fpmDF = mtsb.matchPeaks(fpmDF,mDF,fit,peak_errors['peak-error-third']) 

# Run the compound type abbreviation assignment function – this function takes a passed matched FID and MS list and assigns
# compound type abbreviations to each matched entry
fpmDF = mtsb.ctaAssign(fpmDF, contains, keyloop, element_exclude)

print("[AutoFpmMatch] Handling duplicates...")
#Run the duplicate handling function
fpmDF = mtsb.duplicateHandle(fpmDF)