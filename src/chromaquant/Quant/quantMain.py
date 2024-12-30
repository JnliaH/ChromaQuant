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

def mainQuant(sname,quantphases):

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

    """ DATA IMPORTS """

    print("[quantMain] Importing data...")
    #Import sample information from json file
    with open(os.path.join(directories['data'],sname,sname+'_INFO.json')) as sinfo_f:
        sinfo = json.load(sinfo_f)

    #Change ISO date-time strings into datetime objects
    sinfo['Start Time'] = datetime.fromisoformat(sinfo['Start Time'])
    sinfo['End Time'] = datetime.fromisoformat(sinfo['End Time'])

    #Calculate a reaction time using the start, end, and heat time values and add to sinfo
    sinfo['Reaction Time'] = abs(sinfo['End Time']-sinfo['Start Time']).total_seconds()/3600 - sinfo['Heat Time']

    #Use sample name to form file names using file_suffix and append full pathnames for all entries
    for key in file_suffix:
        file_suffix[key] = [file_suffix[key][0],os.path.join(directories['raw'],sname+file_suffix[key][0])]

    #If the run liquid analysis Boolean is True..
    if lgTF[0]:
        #DEFINE DIRECTORIES FOR LIQUID FID QUANTIFICATION
        #Define directory for liquid matched MS and FID peaks
        DIR_LQ1_FIDpMS = file_suffix['Liquid FID+MS'][1]
        
        #Read matched peak data between liquid FID and MS
        LQ1_FIDpMS = pd.read_csv(DIR_LQ1_FIDpMS)
        
        #Filter FIDpMS to only include rows with non-NaN compounds
        LQ1_FIDpMS_Filtered = LQ1_FIDpMS[LQ1_FIDpMS['Compound Name'].notnull()].reset_index(drop=True)
        
        #Create a duplicate of the FIDpMS dataframe for future saving as a breakdown
        LQ_FID_BreakdownDF = LQ1_FIDpMS_Filtered.copy()
        
        #Read liquid response factors data
        LQRF = {i:pd.read_excel(LRF_path,sheet_name=i) for i in CL_Dict.keys()}

        print("[quantMain] Analyzing liquids...")
        #Get liquid FID breakdown and miscellaneous dataframes
        LQ_FID_BreakdownDF, LQCT_DF, LQCN_DF, LQCTCN_DF, LQmass_DF = qtsb.liquidFID(LQ_FID_BreakdownDF, LQRF, [CL_Dict, CT_Dict], sinfo)
        
        #Insert the carbon number column to LQCTCN_DF
        LQCTCN_DF = qtsb.insertCN(LQCTCN_DF)
        
    else:
        pass

    #If the run gas analysis Boolean is True..
    if lgTF[1]:

        #DEFINE DIRECTORIES FOR GAS TCD AND FID QUANTIFICATION
        
        #Read gas FID and TCD Peak data
        GS2_TCD = pd.read_csv(file_suffix['Gas TCD+FID'][1])
        
        #Create a duplicate of the gas TCD/FID dataframe for future saving as a breakdown
        #Also filter breakdown dataframe to only include rows sourced from TCD
        GS_TCD_BreakdownDF = GS2_TCD.loc[GS2_TCD['Signal Name'] == 'TCD2B'].copy()
        
        #Read matched peak data between gas FID and MS
        GS2_FIDpMS = pd.read_csv(file_suffix['Gas FID+MS'][1])
        
        #Create a duplicate of the FIDpMS dataframe for future saving as a breakdown
        GS_FID_BreakdownDF = GS2_FIDpMS.copy()
        
        #Read gas TCD response factors data
        TCDRF = pd.read_csv(TCDRF_path)
        #Read gas FID response factors data
        GSRF = pd.read_csv(FIDRF_path)

        print("[quantMain] Analyzing gases...")
        #Get gas TCD breakdown and miscellaneous dataframes
        GS_TCD_BreakdownDF, total_volume = qtsb.gasTCD_ES(GS_TCD_BreakdownDF,TCDRF,[gasBag_temp,gasBag_pressure,sinfo['Injected CO2 (mL)']],\
                                                                                    peak_error)
        
        #Get gas FID breakdown and miscellaneous dataframes
        GS_FID_BreakdownDF, GSCT_DF, GSCN_DF, GSCTCN_DF, GSmass_DF = qtsb.gasFID_ES(GS_FID_BreakdownDF,GSRF,\
                                                                                    [CL_Dict, CT_Dict],sinfo,\
                                                                                    [gasBag_temp,gasBag_pressure,sinfo['Injected CO2 (mL)']],\
                                                                                     total_volume)
        
        #Insert the carbon number column to GSCTCN_DF
        GSCTCN_DF = qtsb.insertCN(GSCTCN_DF)

    else:
        pass

    #If both the gas and liquid analysis Booleans are True..
    if lgTF[0] and lgTF[1]:
        print("[quantMain] Totaling contributions from liquid and gas phases...")
        #Get maximum carbon number between breakdown dataframes
        CN_max = max([int(GS_FID_BreakdownDF['Carbon Number'].max()),int(LQ_FID_BreakdownDF['Carbon Number'].max())])
        
        #Sum the liquid and gas breakdown carbon number and compound type dataframes
        #Initiate an empty CTCN dataframe
        total_CTCN_DF = pd.DataFrame({'Aromatics': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                'Linear Alkanes': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                'Branched Alkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                'Cycloalkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                'Alkenes/Alkynes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                'Other':pd.Series(np.empty(CN_max),index=range(CN_max))})


        #For every row in this sum dataframe...
        for i, row in total_CTCN_DF.iterrows():
            #For every entry in this row...
            for j, value in row.items():
                #If the current index is below the carbon number limit of both the gas and liquid dataframes...
                if i <= len(LQCTCN_DF.index)-1 and i <= len(GSCTCN_DF.index)-1:
                    total_CTCN_DF.at[i,j] = LQCTCN_DF.at[i,j] + GSCTCN_DF.at[i,j]
                #Otherwise, if the current index is below the carbon number limit of only the liquid dataframe...
                elif i <= len(LQCTCN_DF.index)-1:
                    total_CTCN_DF.at[i,j] = LQCTCN_DF.at[i,j]
                #Otherwise, if the current index is below the carbon number limit of only the gas dataframe...
                elif i <= len(GSCTCN_DF.index)-1:
                    total_CTCN_DF.at[i,j] = GSCTCN_DF.at[i,j]
                #Otherwise, pass
                else:
                    pass

        #Add the TCD data afterwards
        #Filter the TCD breakdown dataframe to only include entries with non-nan formulas
        GS_TCD_BreakdownDF_filter = GS_TCD_BreakdownDF[GS_TCD_BreakdownDF['Formula'].notnull()]
        #Filter the TCD breakdown dataframe to only include formulas with carbon in them
        GS_TCD_BreakdownDF_filter = GS_TCD_BreakdownDF_filter[(GS_TCD_BreakdownDF_filter['Formula'].str.contains('C')) & (GS_TCD_BreakdownDF_filter['Formula'].str.contains('H'))]
        
        #For every row in this filtered TCD dataframe
        for i, row in GS_TCD_BreakdownDF_filter.iterrows():
            #Get a chemical formula dictionary for the row's formula
            chemFormDict = ChemFormula(row['Formula']).element
            #If the carbon number is less than four...
            if chemFormDict['C'] < 4:
                #Assign the mass value to the linear entry for the given carbon number in the total dataframe
                total_CTCN_DF.at[chemFormDict['C']-1,'Linear Alkanes'] = row['Mass (mg)']
            #Otherwise, if the compound is isobutane...
            elif row['Compound Name'] == 'Isobutane':
                #Add the mass value to the branched entry for carbon number 4 in the total dataframe
                total_CTCN_DF.at[3,'Branched Alkanes'] = row['Mass (mg)']
            #Otherwise, if the compound is butane...
            elif row['Compound Name'] == 'n-Butane':
                #Add the mass value to the linear entry for carbon number 4 in the total dataframe
                total_CTCN_DF.at[3,'Linear Alkanes'] = row['Mass (mg)']
            #Otherwise, pass
            else:
                pass
        
        #Insert the carbon number column to total_CTCN_DF
        total_CTCN_DF = qtsb.insertCN(total_CTCN_DF)
        
    #Otherwise, pass
    else:
        pass

    """ BREAKDOWN SAVING """
    print("[quantMain] Formatting and saving breakdown file...")
    #If breakdown directory does not exist within sample folder, create it
    if not os.path.exists(directories['break']):
        os.makedirs(directories['break'])

    #Get current datetime string
    nows = datetime.now().strftime('%Y%m%d')

    #Define breakdown file name
    bfn = sname+"_Breakdown_"+nows+".xlsx"

    #Create pandas Excel writers
    writer = pd.ExcelWriter(hd.fileCheck(os.path.join(directories['break'],bfn)), engine="xlsxwriter")

    #Get dataframe for sample info
    sinfo_DF = pd.DataFrame(sinfo,index=[0])
        
    #If the run liquid analysis Boolean is True..
    if lgTF[0]:
        #Position the liquid FID dataframes in the worksheet.
        sinfo_DF.to_excel(writer, sheet_name="Liquid FID",startcol=1, startrow=1, index=False) 
        LQ_FID_BreakdownDF.to_excel(writer, sheet_name="Liquid FID",startcol=1, startrow=4, index=False)
        LQCT_DF.to_excel(writer, sheet_name="Liquid FID",startcol=16, startrow=7, index=False)
        LQCN_DF.to_excel(writer, sheet_name="Liquid FID", startcol=16, startrow=15, index=False)
        LQmass_DF.to_excel(writer, sheet_name="Liquid FID",startcol=22, startrow=1,index=False)
        LQCTCN_DF.to_excel(writer, sheet_name="Liquid FID", startcol=20, startrow=7, index=False)
    else:
        pass

    #If the run gas analysis Boolean is True..
    if lgTF[1]:
        #Position the gas FID dataframes in the worksheet.
        sinfo_DF.to_excel(writer, sheet_name="Gas FID",startcol=1, startrow=1, index=False) 
        GS_FID_BreakdownDF.to_excel(writer, sheet_name="Gas FID",startcol=1, startrow=4, index=False)
        GSCT_DF.to_excel(writer, sheet_name="Gas FID",startcol=18, startrow=7, index=False)
        GSCN_DF.to_excel(writer, sheet_name="Gas FID", startcol=18, startrow=15, index=False)
        GSmass_DF.to_excel(writer, sheet_name="Gas FID",startcol=22, startrow=1,index=False)
        GSCTCN_DF.to_excel(writer, sheet_name="Gas FID",startcol=22, startrow=7,index=False)
        
        #Expand sample info dataframe to include total TCD mass and gas bag volume
        sinfo_DF.at[0,'Total product (mg)'] = GS_TCD_BreakdownDF['Mass (mg)'].sum()
        sinfo_DF.at[0,'Gas bag volume (m^3)'] = total_volume
        
        #Position the gas TCD dataframes in the worksheet
        GS_TCD_BreakdownDF.to_excel(writer, sheet_name="Gas TCD",startcol=1,startrow=4, index=False)
        sinfo_DF.to_excel(writer, sheet_name="Gas TCD",startcol=1, startrow=1, index=False) 
    else:
        pass

    #If both the gas and liquid analysis Booleans are True..
    if lgTF[0] and lgTF[1]:
        #Position the total product dataframe in the worksheet
        total_CTCN_DF.to_excel(writer, sheet_name = "Total",startcol=1, startrow=1,index=False)

    #Close the Excel writer
    writer.close()

    print("[quantMain] Quantification complete.")
    #Close main function by returning
    return None

#mainQuant(sname,quantphases)