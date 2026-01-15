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

SCRIPT TO QUANTIFY COMPOUNDS IN SAMPLE USING DEFINED RESPONSE FACTORS

Julia Hancock
Started 12/14/2023

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
import openpyxl

""" QUANTIFICATION MAIN FUNCTION"""
def main_AutoQuantification(sname,quantphases,directories):
    
    print("[AutoQuantification] Evaluating run parameters...")
    #Write whether or not to run liquid and gas analysis based on system argument
    if quantphases == "Liquid":
        #Format is [Liquid Bool, Gas Bool]
        lgTF = [True,False]
    elif quantphases == "Gas":
        lgTF = [False,True]
    elif quantphases == "Liquid and Gas":
        lgTF = [True,True]
    else:
        print("No phases selected, terminating script")
        #Terminate script
        sys.exit()

    print("[AutoQuantification] Defining hard-coded analysis conditions...")
    #Define retention time error within which TCD peaks may be assigned
    peak_error = 0.5

    #Define boolean describing whether or not an external standard was used for gas analysis
    ES_bool = True

    #Define temperature and pressure of gas bag used in sample injection
    gasBag_temp = 18          #C
    gasBag_pressure = 14.7    #psi


    """ RESPONSE FACTOR INFO """
    print("[AutoQuantification] Searching for response factors...")
    #Liquid response factor file name
    LRF_file = "LRF_7-24-24.xlsx"
    #FID gas response factor file name
    GRF_file = "FIDRF_7-24-24.csv"
    #TCD gas response factor file name
    GRFT_file = "TCDRF_7-24-24.csv"

    """ DIRECTORIES """
    print("[AutoQuantification] Finding directories...")

    #Unpack directories from passed variable
    #Primary files directory
    files = directories['files']
    #Resources directory
    RE_Dir = directories['resources']
    #Theme directory
    theme_Dir = directories['theme']
    #Response factor directory
    RF_Dir = directories['rf']
    #Data directory
    DF_Dir = directories['data']
    #Images directory
    img_Dir = directories['images']
    #Data file log directory
    DFlog_Dir = os.path.join(DF_Dir,sname,"log")
    #Data file breakdowns directory
    DFbreak_Dir = os.path.join(DF_Dir,sname,"breakdowns")
    #Raw data file directory
    DFR_Dir = os.path.join(DF_Dir,sname,'raw data')

    """ LOGGING """
    print("[AutoQuantification] Initializing logging [WIP]...")
    #Get current datetime
    now = datetime.now()
    #Get current datetime string
    nows = now.strftime('%Y%m%d')

    #If log directory does not exist within sample folder, create it
    if not os.path.exists(DFlog_Dir):
        os.makedirs(DFlog_Dir)

    #Instantiate a logger
    logger = logging.getLogger(__name__)
    #Initialize logging file using current datetime
    fh = logging.FileHandler(os.path.join(DFlog_Dir,'quantlog_'+nows+'.log'))
    logger.addHandler(fh)
    logger.propagate = False
    #Set logging level
    logger.setLevel(logging.INFO)
    #Create a formatter and assign to logger
    formatter = logging.Formatter('[%(filename)s] %(asctime)s - [%(levelname)s]: %(message)s')
    fh.setFormatter(formatter)


    """ LABELS """
    print("[AutoQuantification] Defining chemical lumps and compound types...")
    #Dictionary of all chemical lump abbreviations in use and their associated expansions
    #OLD DICTIONARY
    #CL_Dict = {'MBE':'Methyl benzenes', 'ABE':'Alkyl benzenes', 'NAP':'Napthalenes', 'MAL':'Methl alkanes',
    #           'DAL':'Dimethyl alkanes','TAL':'Trimethyl alkanes','MCA':'Methyl cycloalkanes','ACA':'Alkyl cycloalkanes',
    #           'AAL':'Alkyl alkanes','MAE':'Methyl alkenes','DAE':'Dimethyl alkenes','AAE':'Alkyl alkenes',
    #           'LAL':'Linear alkanes','CAE':'Cycloalkenes','IND':'Indenes','PAH':'Polycyclic aromatic hydrocarbons',
    #           'AKY':'Alkynes'}

    #7-24-24: Could have removed the CL_Dict infrastructure, but nice to have in place in case we want to
    #add more complexity to response factor assignment later

    #Dictionary of all compound type abbreviations in use and their associated expansions
    CL_Dict = {'A':'Aromatics','L':'Linear Alkanes','B':'Branched Alkanes',
            'C':'Cycloalkanes','E':'Alkenes/Alkynes'}

    #Alphabetize lump abbreviation dictionary
    CL_Dict = dict(sorted(CL_Dict.items()))

    #Dictionary of all compound type abbreviations in use and their associated expansions
    CT_Dict = {'A':'Aromatics','L':'Linear Alkanes','B':'Branched Alkanes',
            'C':'Cycloalkanes','E':'Alkenes/Alkynes','O':'Other'}

    #Alphabetize compound type abbreviation dictionary
    CT_Dict = dict(sorted(CT_Dict.items()))

    """ FUNCTIONS """
    print("[AutoQuantification] Defining functions...")
    #Function for checking if file exists and adding number if so
    def fileCheck(path):
        #Inspired by https://stackoverflow.com/questions/13852700/create-file-but-if-name-exists-add-number
        filename, extension = os.path.splitext(path)
        i = 1
        
        while os.path.exists(path):
            path = filename + " ("+str(i)+")" + extension
            i += 1
        
        return path
    
    #Function for quantifying liquid FID data
    def liquidFID(BreakdownDF,DBRF,Label_info,sinfo):
        
        #Unpack compound type and carbon number dictionaries from list
        CL_Dict, CT_Dict = Label_info
        
        """ FUNCTIONS """
        #Function to assign compound type and carbon number to compound using formula
        def assignCTCN(BreakdownDF,CT_dict):
            #Iterate through every species in the breakdown dataframe and add entries in two new columns: Compound Type and Carbon Number
            for i, row in BreakdownDF.iterrows():
                #If there exists a formula..
                try:
                    #Set breakdown compound type according to the abbreviation already in the breakdown dataframe
                    BreakdownDF.at[i,'Compound Type'] = CT_dict[BreakdownDF.at[i,'Compound Type Abbreviation']]
                    #Obtain a dictionary containing key:value pairs as element:count using the formula string for the ith row
                    chemFormDict = ChemFormula(row['Formula']).element
                    #Use the carbon entry from the above dictionary to assign a carbon number to the ith row
                    BreakdownDF.at[i,'Carbon Number'] = chemFormDict['C']
                #Otherwise, pass
                except:
                    pass
            
            return BreakdownDF
        
        #Function to assign response factor by carbon number and compound type
        def assignRF(BreakdownDF,DBRF,CL_Dict):
            """
            Function takes a dataframe containing matched FID and MS peak information and
            compares it against a provided response factor database to assign response
            factors to the matched peak dataframe.
            
            Parameters
            ----------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data
            
            DBRF : Dataframe
                Dataframe containing nested dataframes with associated chemical lumps,
                likely imported from an excel sheet where each sheet is specific to
                a given chemical lump. The top-level keys must be associated with the
                predefined chemical lumps given in 'LABELS' section above
            
            CL_Dict : Dict
                Dictionary containing key:value pairs defined as 
                (chemical lump abbreviation):(full chemical lump name)
            
            Returns
            -------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data
        
            """
            #Define an initial response factor
            RF = 1
        
            #Loop through every labelled peak in the breakdown DataFrame
            for i, row in BreakdownDF.iterrows():
                #Find the compound name, carbon number, and compound type abbreviation
                cmp_name = row['Compound Name']
                cmp_carbon = row['Carbon Number']
                cmp_type = row['Compound Type Abbreviation']
                
                #If any of these pieces of infomation is NAN, skip the row and set the RF Source accordingly
                if pd.isna(cmp_name) or pd.isna(cmp_carbon) or pd.isna(cmp_type):
                    BreakdownDF.at[i,'RF Source'] = 'No RF assigned, at least one of the following were missing: compound name, formula, or type abbreviation'
                    pass
                
                #Or, if the compound type is Other, "O", skip the row and set the RF source accordingly
                elif cmp_type == "O":
                    BreakdownDF.at[i,'RF Source'] = 'No RF assigned, compound type is listed as "Other"'
                    pass
                
                #Otherwise...
                else:
                    #If the compound name is in the sheet corresponding to the compound type abbreviation..
                    if cmp_name in list(DBRF[cmp_type]['Compound Name'].values):
                            
                        #Get the response factors sheet index where it is listed
                        dbrf_index = DBRF[cmp_type].index[DBRF[cmp_type]['Compound Name'] == cmp_name]
                        
                        #Assign the listed response factor in the matched sheet to the RF variable
                        RF = DBRF[cmp_type].loc[dbrf_index,'Response Factor'].iloc[0]
                            
                        #If the listed RF is nan...
                        if math.isnan(RF):
                            #Set the RF to 1
                            RF = 1
                            #Set the value for response factor in the breakdown dataframe to RF
                            BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                            #Set the RF source
                            BreakdownDF.at[i,'RF Source'] = 'Assumed 1, compound found in RF sheet without RF'
                        
                        #Otherwise...
                        else:
                            #Set the value for response factor in the breakdown dataframe to RF
                            BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                            #Set the RF source
                            BreakdownDF.at[i,'RF Source'] = 'Assigned empirical RF, exact compound found in response factors sheet'
                    
                    #Otherwise, if the compound name is not in the sheet...
                    else:
                        
                        #Get the m and b parameters listed in the RF linear fit for that compound type
                        fit_m = DBRF[cmp_type].loc[0,'Linear fit m']
                        fit_b = DBRF[cmp_type].loc[0,'Linear fit b']
                        
                        #If both the m and b parameters are nan, assign a response factor of 1
                        if math.isnan(fit_m) and math.isnan(fit_b):
                            #Set the RF to 1
                            RF = 1
                            #Set the value for response factor in the breakdown dataframe to RF
                            BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                            #Set the RF source to
                            BreakdownDF.at[i,'RF Source'] = 'Assumed 1, compound type does not have a carbon number fit'
                            
                        #Otherwise, assign a response factor by carbon number
                        else:
                            #Get response factor using fit and carbon number
                            RF = fit_m*cmp_carbon+fit_b
                            
                            #If the estimated response factor is negative or larger than 5, set RF to 1
                            if RF < 0 or RF > 5:
                                RF = 1
                                #Set the value for response factor in the breakdown dataframe to RF
                                BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                                #Set the RF source to "Assumed 1, estimated response factor exists but is out of range"
                                BreakdownDF.at[i,'RF Source'] = 'Assumed 1, could estimate a response factor exists but is out of range (negative or over 5)'
                                
                            #Otherwise...
                            else:
                                #Set the value for response factor in the breakdown dataframe to RF
                                BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                                #Set the RF source
                                BreakdownDF.at[i,'RF Source'] = 'Assigned using carbon number linear fit for compound type {0} and carbon number {1}'.format(cmp_type,int(cmp_carbon))
                
            return BreakdownDF
        
        def quantMain(BreakdownDF,sinfo):
            """
            Function that takes in matched FID and MS data with assigned response factors
            and returns quantitative data
            
            Parameters
            ----------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
            IS_m : Int
                Amount of internal standard added to sample in mg.
            IS_name : Str
                Name of internal standard added to sample
                
            Returns
            -------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
        
            """
            #Get IS_m and IS_name from sinfo
            IS_m, IS_name = [sinfo['Internal Standard Mass (mg)'],sinfo['Internal Standard Name']]
            #Find the index where the internal standard is listed – if it's listed more than once, take the largest area peak
            IS_index = BreakdownDF[BreakdownDF['Compound Name'] == IS_name]['FID Area'].idxmax()
            
            #Get the FID area associated with the internal standard
            IS_Area = BreakdownDF.at[IS_index,'FID Area']
            
            #Loop through breakdown dataframe, calculating an area ratio and mass for each row
            for i, row in BreakdownDF.iterrows():
                #If the row's compound name is the internal standard name or either form of no match, skip the row
                if row['Compound Name'] == IS_name or row['Compound Name'] == 'No match' or row['Compound Name'] == 'No Match':
                    pass
                #Otherwise, continue
                else:
                    #Calculate area ratio
                    Aratio = row['FID Area']/IS_Area
                    #Calculate mass using response factor column
                    m_i = Aratio*IS_m/row['Response Factor ((A_i/A_T)/(m_i/m_T))']
                    #Assign area ratio and mass to their respective columns in the breakdown dataframe
                    BreakdownDF.at[i,'A_i/A_T'] = Aratio
                    BreakdownDF.at[i,'m_i'] = m_i
            
            return BreakdownDF
        
        def moreBreakdown(BreakdownDF,CT_dict,sinfo):
            """
            This function prepares further breakdown dictionaries for use in exporting to Excel
        
            Parameters
            ----------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
            CT_dict : Dict
                Dictionary of all compound type abbreviations in use and their associated expansions
            sinfo : Dict
                Dictionary containing sample information.
                
            Returns
            -------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
        
            """
            
            #Get the total mass of product from the breakdown dataframe
            m_total = np.nansum(BreakdownDF['m_i'])
            
            #Get maximum carbon number in breakdown dataframe
            CN_max = int(BreakdownDF['Carbon Number'].max())
        
            #Create a dataframe for saving quantitative results organized by compound type
            CT_DF = pd.DataFrame({'Compound Type':['Aromatics','Linear Alkanes','Branched Alkanes',
                                                        'Cycloalkanes','Alkenes/Alkynes','Other'],
                                        'Mass (mg)':np.empty(6),
                                        'Mass fraction':np.empty(6)})
            
            #Create a dataframe for saving quantitative results organized by carbon number
            CN_DF = pd.DataFrame({'Carbon Number':range(1,CN_max+1,1),
                                        'Mass (mg)':np.empty(CN_max)})
            
            #Create a dataframe for saving quantitative results organized by both compound type and carbon number
            CTCN_DF = pd.DataFrame({'Aromatics': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Linear Alkanes': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Branched Alkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Cycloalkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Alkenes/Alkynes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Other':pd.Series(np.empty(CN_max),index=range(CN_max))})
            
            #Iterate through every compound type in the compound type dataframe, summing the total respective masses from the breakdown dataframe
            for i, row in CT_DF.iterrows():
                
                #Define a temporary dataframe which contains all rows matching the ith compound type
                tempDF = BreakdownDF.loc[BreakdownDF['Compound Type'] == row['Compound Type']]
                #Assign the ith compound type's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                CT_DF.at[i,'Mass (mg)'] = np.nansum(tempDF['m_i'])
                #Calculate and assign the ith compound type's mass fraction usingthe total mass from earlier
                CT_DF.at[i,'Mass fraction'] = CT_DF.at[i,'Mass (mg)']/m_total
            
            #Iterate through every carbon number in the carbon number dataframe, summing the total respective masses from the breakdown dataframe
            for i, row in CN_DF.iterrows():
                
                #Define a temporary dataframe which contains all rows matching the ith carbon number
                tempDF = BreakdownDF.loc[BreakdownDF['Carbon Number'] == row['Carbon Number']]
                #Assign the ith carbon number's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                CN_DF.at[i,'Mass (mg)'] = np.nansum(tempDF['m_i'])
            
            #Iterate through the entire dataframe, getting masses for every compound type - carbon number pair
            for i, row in CTCN_DF.iterrows():
                
                #For every entry in row
                for j in row.index:
                    
                    #Define a temporary dataframe which contains all rows matching the ith carbon number and compound type
                    tempDF = BreakdownDF.loc[(BreakdownDF['Carbon Number'] == i+1) & (BreakdownDF['Compound Type'] == j)]
                    #Assign the ith carbon number/jth compound type's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                    CTCN_DF.loc[i,j] = np.nansum(tempDF['m_i'])
                    
                    
            #Get total masses from CT, CN, and CTCN dataframes
            CT_mass = np.nansum(CT_DF['Mass (mg)'])
            CN_mass = np.nansum(CN_DF['Mass (mg)'])
            CTCN_mass = np.nansum(CTCN_DF)
            
            #Create total mass dataframe
            mass_DF = pd.DataFrame({'Total mass source':['Overall breakdown','Compound Type Breakdown','Carbon Number Breakdown','Compound Type + Carbon Number Breakdown'],'Mass (mg)':[m_total,CT_mass,CN_mass,CTCN_mass]})
            
            return BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF
        
        """ BREAKDOWN FORMATION """
        
        #Use the assignCTCN function to assign compound type and carbon number
        BreakdownDF = assignCTCN(BreakdownDF,CT_Dict)
        
        #Use the assignRF function to assign response factors, preferring empirical RF's to estimated ones and assigning 1 when no other RF can be applied
        BreakdownDF = assignRF(BreakdownDF,DBRF,CL_Dict)

        #Use the quantMain function to add quantitative data to BreakdownDF
        BreakdownDF = quantMain(BreakdownDF,sinfo)

        #Use the moreBreakdown function to prepare compound type and carbon number breakdowns
        BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF = moreBreakdown(BreakdownDF,CT_Dict,sinfo)
        
        return [BreakdownDF,CT_DF,CN_DF,CTCN_DF,mass_DF,]

    #Function for quantifying gas TCD data w/o external standard
    def gasTCD(BreakdownDF,DBRF,sinfo,peak_error):
        
        #Add min and max peak assignment values to DBRF
        for i, row in DBRF.iterrows():
            DBRF.at[i,'RT Max'] = DBRF.at[i,'RT (min)'] + peak_error
            DBRF.at[i,'RT Min'] = DBRF.at[i,'RT (min)'] - peak_error
            
        #Unpack sinfo to get local variables
        vol = sinfo['Reactor Volume (mL)']          #reactor volume, mL
        pressure = sinfo['Quench Pressure (psi)']   #sample pressure, psi
        temp = sinfo['Quench Temperature (C)']      #sample temperature, C
        
        #Convert sinfo variables to new units
        vol = vol / 10**6                     #reactor volume, m^3
        pressure = pressure / 14.504*100000   #reactor pressure, Pa
        temp = temp + 273.15                  #reactor temperature, K
        
        #Define ideal gas constant, m^3*Pa/K*mol
        R = 8.314
        
        #Iterate through every row in BreakdownDF
        for i, row in BreakdownDF.iterrows():
            
            #Iterate through every row in DBRF
            for i2, row2 in DBRF.iterrows():
                
                #If the TCD response factor is within the range for a given DBRF entry..
                if row2['RT Min'] <= row['RT'] <= row2['RT Max']:
                    
                    #Add the compound name to the breakdown dataframe
                    BreakdownDF.at[i,'Compound Name'] = row2['Compound Name']
                    
                    #Add the other relevant information to the breakdown dataframe
                    BreakdownDF.at[i,'Formula'] = row2['Formula']
                    BreakdownDF.at[i,'RF (Area/vol.%)'] = row2['RF']
                    BreakdownDF.at[i,'MW (g/mol)'] = ChemFormula(row2['Formula']).formula_weight
                    
                    #Get volume percent using response factor
                    BreakdownDF.at[i,'Vol.%'] = row['Area']/row2['RF']
                    
                    #Get moles using ideal gas law (PV=nRT)
                    BreakdownDF.at[i,'Moles'] = BreakdownDF.at[i,'Vol.%']/100*vol*pressure/(temp*R)
                    
                    #Get mass (mg) using moles and molar mass
                    BreakdownDF.at[i,'Mass (mg)'] = BreakdownDF.at[i,'Moles'] * BreakdownDF.at[i,'MW (g/mol)'] * 1000
                
                #Otherwise, pass    
                else:
                    pass
                
        return BreakdownDF, DBRF, [vol, pressure, temp]

    #Function for quantifying gas TCD data w/ external standard
    def gasTCD_ES(BreakdownDF,DBRF,sinfo,gasBag_cond,peak_error):
        
        #Unpack gas bag conditions
        temp = gasBag_cond[0]       #temperature of gas bag, C
        pressure = gasBag_cond[1]   #sample pressure in gas bag, psi
        
        #Initialize compound name column in BreakdownDF
        BreakdownDF['Compound Name'] = 'None'
        
        #Function to find if CO2 peak exists
        def getCO2(BreakdownDF,DBRF,TCD_cond,peak_error):
            
            #Unpack TCD conditions
            co2 = TCD_cond[0]
            pressure = TCD_cond[1]
            temp = TCD_cond[2]
            R = TCD_cond[3]
            
            #Find the CO2 peak row in DBRF
            CO2_row = DBRF.loc[DBRF['Compound Name'] == "Carbon Dioxide"].iloc[0]
            
            #Get the retention time
            CO2_RT = CO2_row['RT (min)']
            
            #Get the minimum and maximum of the RT range using the peak error
            CO2_RTmin = CO2_RT - peak_error
            CO2_RTmax = CO2_RT + peak_error
            
            #Define boolean describing whether or not CO2 match has been found
            CO2_bool = False
            #Define volume estimate
            volume = 0
            
            #Iterate through every row in BreakdownDF
            for i, row in BreakdownDF.iterrows():
                
                #If the TCD retention time is within range of the CO2 entry...
                if CO2_RTmin <= row['RT'] <= CO2_RTmax:
                    
                    #Add the compound name to the breakdown dataframe
                    BreakdownDF.at[i,'Compound Name'] = 'Carbon Dioxide'
                    
                    #Add the other relevant information to the breakdown dataframe
                    BreakdownDF.at[i,'Formula'] = 'CO2'
                    BreakdownDF.at[i,'RF (Area/vol.%)'] = CO2_row['RF']
                    BreakdownDF.at[i,'MW (g/mol)'] = ChemFormula('CO2').formula_weight
                    
                    #Get volume percent using response factor
                    volpercent = row['Area']/CO2_row['RF']
                    BreakdownDF.at[i,'Vol.%'] = volpercent
                    
                    #Calculate total volume using volume percent
                    volume = co2 * 100 / volpercent   #total volume, m^3
                    
                    #Assign CO2 volume
                    BreakdownDF.at[i,'Volume (m^3)'] = co2
                    
                    #Get moles using ideal gas law (PV=nRT)
                    BreakdownDF.at[i,'Moles (mol)'] = co2*pressure/(temp*R)
                    
                    #Get mass (mg) using moles and molar mass
                    BreakdownDF.at[i,'Mass (mg)'] = BreakdownDF.at[i,'Moles (mol)'] * BreakdownDF.at[i,'MW (g/mol)'] * 1000
                    
                    #Set CO2_bool to True
                    CO2_bool = True
                    
                    break
                
                #Otherwise, pass
                else:
                    pass
            
            return CO2_bool, volume, BreakdownDF
        
        #Add min and max peak assignment values to DBRF
        for i, row in DBRF.iterrows():
            DBRF.at[i,'RT Max'] = DBRF.at[i,'RT (min)'] + peak_error
            DBRF.at[i,'RT Min'] = DBRF.at[i,'RT (min)'] - peak_error
            
        #Unpack sinfo to get CO2 injection volume
        co2 = sinfo['Injected CO2 (mL)']            #volume injected CO2, mL
        
        #Convert sinfo variables to new units
        co2 = co2 / 10**6                     #volume injected CO2, mL
        temp = temp + 273.15                  #reactor temperature, K
        pressure = pressure / 14.504*100000   #reactor pressure, Pa
        
        #Define ideal gas constant, m^3*Pa/K*mol
        R = 8.314
        
        #Define variable to total volume (m^3)
        volume = 0
        
        #Define list of conditions
        TCD_cond = [co2,pressure,temp,R]
        
        #Check if there is a peak in the BreakdownDF that can be assigned to CO2
        CO2_bool, volume, BreakdownDF = getCO2(BreakdownDF,DBRF,TCD_cond,peak_error)
        
        if CO2_bool:
            #Iterate through every row in BreakdownDF
            for i, row in BreakdownDF.iterrows():
                
                #Iterate through every row in DBRF
                for i2, row2 in DBRF.iterrows():
                    
                    #If the TCD retention time is within the range for a given DBRF entry...
                    if row2['RT Min'] <= row['RT'] <= row2['RT Max']:
                        
                        #Add the compound name to the breakdown dataframe
                        BreakdownDF.at[i,'Compound Name'] = row2['Compound Name']
                        
                        #Add the other relevant information to the breakdown dataframe
                        BreakdownDF.at[i,'Formula'] = row2['Formula']
                        BreakdownDF.at[i,'RF (Area/vol.%)'] = row2['RF']
                        BreakdownDF.at[i,'MW (g/mol)'] = ChemFormula(row2['Formula']).formula_weight
                        
                        #Get volume percent using response factor
                        volpercent = row['Area']/row2['RF']
                        BreakdownDF.at[i,'Vol.%'] = volpercent
                        
                        #Get volume using volume percent
                        vol = volume*volpercent/100
                        BreakdownDF.at[i,'Volume (m^3)'] = vol
                        
                        #Get moles using ideal gas law (PV=nRT)
                        BreakdownDF.at[i,'Moles (mol)'] = vol*pressure/(temp*R)
                        
                        #Get mass (mg) using moles and molar mass
                        BreakdownDF.at[i,'Mass (mg)'] = BreakdownDF.at[i,'Moles (mol)'] * BreakdownDF.at[i,'MW (g/mol)'] * 1000
                    
                    #Otherwise, pass    
                    else:
                        pass
        #Otherwise, pass
        else:
            pass
        
        return BreakdownDF, DBRF, volume, TCD_cond

    #Function for quantifying gas FID data w/o external standard
    def gasFID(BreakdownDF,DBRF,Label_info,sinfo,cutoff=4):
        """
        Function quantifies gas FID data and returns a breakdown dataframe

        Parameters
        ----------
        BreakdownDF : DataFrame
            Dataframe containing columns associated with matched FID and MS peak data
        DBRF : Dataframe
            Dataframe containing nested dataframes with associated chemical lumps,
            likely imported from an excel sheet where each sheet is specific to
            a given chemical lump. The top-level keys must be associated with the
            predefined chemical lumps given in 'LABELS' section above
        Label_info : List
            List of dictionaries containing chemical lump and compound type abbreviations
        sinfo : Dict
            Dictionary containing key sample information
        cutoff : Integer, optional
            Integer representing the maximum cutoff carbon number that can be 
            quantified using FID.The default is 4.

        Returns
        -------
        BreakdownDF : DataFrame
            Dataframe containing columns associated with matched FID and MS peak data

        """
        #Function for assigning response factors to compounds
        def assignRF(BreakdownDF,DBRF):
            
            #Get a dictionary of average response factors by carbon number
            avgRF = {}
            #Loop through every carbon number up to the max in DBRF
            for i in range(1,DBRF['Carbon Number'].max()+1):
                #Get a slice of all rows in DBRF with a given carbon number
                slicer = DBRF.loc[DBRF['Carbon Number']==i]
                #Average the response factor entries in this slice, appending the result to the average RF dictionary
                avgRF['{0}'.format(i)] = slicer['RF'].mean()
                
            #Loop through every row in the FIDpMS dataframe
            for i, row in BreakdownDF.iterrows():
                #Check that the formula is not nan
                if not pd.isna(row['Formula']):
                    #Obtain a dictionary containing key:value pairs as element:count using the formula string for the ith row
                    chemFormDict = ChemFormula(row['Formula']).element
                    #Use the carbon entry from the above dictionary to assign a carbon number to the ith row
                    BreakdownDF.at[i,'Carbon Number'] = chemFormDict['C']
                
                    #If the row's compound name exists in the RF list explicitly, assign the row to the appropriate RF
                    if row['Compound Name'] in DBRF['Compound Name'].values:
                        BreakdownDF.at[i,'RF (Area/vol.%)'] = DBRF.loc[DBRF['Compound Name']==row['Compound Name'],'RF'].iloc[0]
                        #Assign response factor source
                        BreakdownDF.at[i,'RF Source'] = 'Direct RF assignment based on compound name'
                    #Otherwise, assign response factor based on average carbon number RF
                    else:
                        BreakdownDF.at[i,'RF (Area/vol.%)'] = avgRF['{0}'.format(int(BreakdownDF.at[i,'Carbon Number']))]
                        #Assign response factor source
                        BreakdownDF.at[i,'RF Source'] = 'RF assignment based on average response factor for DBRF carbon number entries'
                #Otherwise if the row's formula is nan, pass
                else:
                    pass
                
                
            return BreakdownDF
        
        #Function for quantifying compounds using ideal gas law
        def gasQuant(BreakdownDF,DBRF,sinfo,cutoff):
            
            #Remove columns in BreakdownDF with a carbon number at or below cutoff
            BreakdownDF = BreakdownDF.loc[BreakdownDF['Carbon Number'] > cutoff].copy()
            
            #Unpack sinfo to get local variables
            vol = sinfo['Reactor Volume (mL)']          #reactor volume, mL
            pressure = sinfo['Quench Pressure (psi)']   #sample pressure, psi
            temp = sinfo['Quench Temperature (C)']      #sample temperature, C
            
            #Convert sinfo variables to new units
            vol = vol / 10**6                     #reactor volume, m^3
            pressure = pressure / 14.504*100000   #reactor pressure, Pa
            temp = temp + 273.15                  #reactor temperature, K
            
            #Define ideal gas constant, m^3*Pa/K*mol
            R = 8.314
            
            #Loop through every row in BreakdownDF
            for i, row in BreakdownDF.iterrows():
                
                #Add molecular weight using ChemFormula
                BreakdownDF.at[i,'MW (g/mol)'] = ChemFormula(row['Formula']).formula_weight
                
                #Get volume percent using response factor
                BreakdownDF.at[i,'Vol.%'] = row['FID Area']/row['RF (Area/vol.%)']
                
                #Get moles using ideal gas law (PV=nRT)
                BreakdownDF.at[i,'Moles'] = BreakdownDF.at[i,'Vol.%']/100*vol*pressure/(temp*R)
                
                #Get mass (mg) using moles and molar mass
                BreakdownDF.at[i,'Mass (mg)'] = BreakdownDF.at[i,'Moles'] * BreakdownDF.at[i,'MW (g/mol)'] * 1000
                
            return BreakdownDF
        
        #Function for further breaking down product distribution
        def moreBreakdown(BreakdownDF,CT_dict,sinfo):
            """
            This function prepares further breakdown dictionaries for use in exporting to Excel
        
            Parameters
            ----------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
            CT_dict : Dict
                Dictionary of all compound type abbreviations in use and their associated expansions
            sinfo : Dict
                Dictionary containing sample information.
                
            Returns
            -------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
        
            """
            
            #Get the total mass of product from the breakdown dataframe
            m_total = np.nansum(BreakdownDF['Mass (mg)'])
            
            #Iterate through every species in the breakdown dataframe and add entries in two new columns: Compound Type and Carbon Number
            for i, row in BreakdownDF.iterrows():
                #If there exists a formula..
                try:
                    #Set breakdown compound type according to the abbreviation already in the breakdown dataframe
                    BreakdownDF.at[i,'Compound Type'] = CT_dict[BreakdownDF.at[i,'Compound Type Abbreviation']]
                    #Obtain a dictionary containing key:value pairs as element:count using the formula string for the ith row
                    chemFormDict = ChemFormula(row['Formula']).element
                    #Use the carbon entry from the above dictionary to assign a carbon number to the ith row
                    BreakdownDF.at[i,'Carbon Number'] = chemFormDict['C']
                #Otherwise, pass
                except:
                    pass
            
            #Get maximum carbon number in breakdown dataframe
            CN_max = int(BreakdownDF['Carbon Number'].max())
        
            #Create a dataframe for saving quantitative results organized by compound type
            CT_DF = pd.DataFrame({'Compound Type':['Aromatics','Linear Alkanes','Branched Alkanes',
                                                        'Cycloalkanes','Alkenes/Alkynes','Other'],
                                        'Mass (mg)':np.empty(6),
                                        'Mass fraction':np.empty(6)})
            
            #Create a dataframe for saving quantitative results organized by carbon number
            CN_DF = pd.DataFrame({'Carbon Number':range(1,CN_max+1,1),
                                        'Mass (mg)':np.empty(CN_max)})
            
            #Create a dataframe for saving quantitative results organized by both compound type and carbon number
            CTCN_DF = pd.DataFrame({'Aromatics': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Linear Alkanes': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Branched Alkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Cycloalkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Alkenes/Alkynes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Other':pd.Series(np.empty(CN_max),index=range(CN_max))})
            
            #Iterate through every compound type in the compound type dataframe, summing the total respective masses from the breakdown dataframe
            for i, row in CT_DF.iterrows():
                
                #Define a temporary dataframe which contains all rows matching the ith compound type
                tempDF = BreakdownDF.loc[BreakdownDF['Compound Type'] == row['Compound Type']]
                #Assign the ith compound type's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                CT_DF.at[i,'Mass (mg)'] = np.nansum(tempDF['Mass (mg)'])
                #Calculate and assign the ith compound type's mass fraction usingthe total mass from earlier
                CT_DF.at[i,'Mass fraction'] = CT_DF.at[i,'Mass (mg)']/m_total
            
            #Iterate through every carbon number in the carbon number dataframe, summing the total respective masses from the breakdown dataframe
            for i, row in CN_DF.iterrows():
                
                #Define a temporary dataframe which contains all rows matching the ith carbon number
                tempDF = BreakdownDF.loc[BreakdownDF['Carbon Number'] == row['Carbon Number']]
                #Assign the ith carbon number's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                CN_DF.at[i,'Mass (mg)'] = np.nansum(tempDF['Mass (mg)'])
            
            #Iterate through the entire dataframe, getting masses for every compound type - carbon number pair
            for i, row in CTCN_DF.iterrows():
                
                #For every entry in row
                for j in row.index:
                    
                    #Define a temporary dataframe which contains all rows matching the ith carbon number and compound type
                    tempDF = BreakdownDF.loc[(BreakdownDF['Carbon Number'] == i+1) & (BreakdownDF['Compound Type'] == j)]
                    #Assign the ith carbon number/jth compound type's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                    CTCN_DF.loc[i,j] = np.nansum(tempDF['Mass (mg)'])
                    
                    
            #Get total masses from CT, CN, and CTCN dataframes
            CT_mass = np.nansum(CT_DF['Mass (mg)'])
            CN_mass = np.nansum(CN_DF['Mass (mg)'])
            CTCN_mass = np.nansum(CTCN_DF)
            
            #Create total mass dataframe
            mass_DF = pd.DataFrame({'Total mass source':['Overall breakdown','Compound Type Breakdown','Carbon Number Breakdown','Compound Type + Carbon Number Breakdown'],'Mass (mg)':[m_total,CT_mass,CN_mass,CTCN_mass]})
            
            return BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF
        
        #Unpack compound type and carbon number dictionaries from list
        CL_Dict, CT_Dict = Label_info
        
        #Filter dataframe to remove compounds that do not contain carbon
        BreakdownDF = BreakdownDF.drop(BreakdownDF[[not i for i in BreakdownDF['Formula'].str.contains('C')]].index)
        #Reset the dataframe index
        BreakdownDF.reset_index()
        
        #Run response factor assignment function
        BreakdownDF = assignRF(BreakdownDF, DBRF)
        #Run gas quantification function
        BreakdownDF = gasQuant(BreakdownDF,DBRF,sinfo,cutoff)
        #Run further breakdown function
        BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF = moreBreakdown(BreakdownDF, CT_Dict, sinfo)
        
        return BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF

    #Function for quantifying gas FID data w/ external standard
    def gasFID_ES(BreakdownDF,DBRF,Label_info,sinfo,gasBag_cond,total_volume,cutoff=4):
        """
        Function quantifies gas FID data and returns a breakdown dataframe

        Parameters
        ----------
        BreakdownDF : DataFrame
            Dataframe containing columns associated with matched FID and MS peak data
        DBRF : Dataframe
            Dataframe containing nested dataframes with associated chemical lumps,
            likely imported from an excel sheet where each sheet is specific to
            a given chemical lump. The top-level keys must be associated with the
            predefined chemical lumps given in 'LABELS' section above
        Label_info : List
            List of dictionaries containing chemical lump and compound type abbreviations
        sinfo : Dict
            Dictionary containing key sample information
        total_volume : Float
            Float describing the total amount of gas estimated by the external standard volume percent
        cutoff : Integer, optional
            Integer representing the maximum cutoff carbon number that can be 
            quantified using FID.The default is 4.

        Returns
        -------
        BreakdownDF : DataFrame
            Dataframe containing columns associated with matched FID and MS peak data

        """
        #Function for assigning response factors to compounds
        def assignRF(BreakdownDF,DBRF):
            
            #Get a dictionary of average response factors by carbon number
            avgRF = {}
            #Loop through every carbon number up to the max in DBRF
            for i in range(1,DBRF['Carbon Number'].max()+1):
                #Get a slice of all rows in DBRF with a given carbon number
                slicer = DBRF.loc[DBRF['Carbon Number']==i]
                #Average the response factor entries in this slice, appending the result to the average RF dictionary
                avgRF['{0}'.format(i)] = slicer['RF'].mean()
                
            #Loop through every row in the FIDpMS dataframe
            for i, row in BreakdownDF.iterrows():
                #Check that the formula is not nan
                if not pd.isna(row['Formula']):
                    #Obtain a dictionary containing key:value pairs as element:count using the formula string for the ith row
                    chemFormDict = ChemFormula(row['Formula']).element
                    #Use the carbon entry from the above dictionary to assign a carbon number to the ith row
                    BreakdownDF.at[i,'Carbon Number'] = chemFormDict['C']
                
                    #If the row's compound name exists in the RF list explicitly, assign the row to the appropriate RF
                    if row['Compound Name'] in DBRF['Compound Name'].values:
                        BreakdownDF.at[i,'RF (Area/vol.%)'] = DBRF.loc[DBRF['Compound Name']==row['Compound Name'],'RF'].iloc[0]
                        #Assign response factor source
                        BreakdownDF.at[i,'RF Source'] = 'Direct RF assignment based on compound name'
                    #Otherwise, assign response factor based on average carbon number RF
                    else:
                        BreakdownDF.at[i,'RF (Area/vol.%)'] = avgRF['{0}'.format(int(BreakdownDF.at[i,'Carbon Number']))]
                        #Assign response factor source
                        BreakdownDF.at[i,'RF Source'] = 'RF assignment based on average response factor for DBRF carbon number entries'
                #Otherwise if the row's formula is nan, pass
                else:
                    pass
                
                
            return BreakdownDF
        
        #Function for quantifying compounds using ideal gas law
        def gasQuant(BreakdownDF,DBRF,sinfo,total_volume,cutoff):
            
            #Remove rows in BreakdownDF with a carbon number at or below cutoff
            BreakdownDF = BreakdownDF.loc[BreakdownDF['Carbon Number'] > cutoff].copy()
            
            #Get gas bag conditions
            temp = gasBag_cond[0]       #temperature of gas bag, C
            pressure = gasBag_cond[1]   #sample pressure in gas bag, psi
            
            #Convert sinfo variables to new units
            temp = temp + 273.15                    #gas bag temperature, K
            pressure = pressure / 14.504*100000     #gas bag pressure, Pa
            
            #Define ideal gas constant, m^3*Pa/K*mol
            R = 8.314
            
            #Loop through every row in BreakdownDF
            for i, row in BreakdownDF.iterrows():
                
                #Add molecular weight using ChemFormula
                BreakdownDF.at[i,'MW (g/mol)'] = ChemFormula(row['Formula']).formula_weight
                
                #Get volume percent using response factor
                BreakdownDF.at[i,'Vol.%'] = row['FID Area']/row['RF (Area/vol.%)']
                
                #Get moles using ideal gas law (PV=nRT)
                BreakdownDF.at[i,'Moles'] = BreakdownDF.at[i,'Vol.%']/100*total_volume*pressure/(temp*R)
                
                #Get mass (mg) using moles and molar mass
                BreakdownDF.at[i,'Mass (mg)'] = BreakdownDF.at[i,'Moles'] * BreakdownDF.at[i,'MW (g/mol)'] * 1000
                
            return BreakdownDF
        
        #Function for further breaking down product distribution
        def moreBreakdown(BreakdownDF,CT_dict,sinfo):
            """
            This function prepares further breakdown dictionaries for use in exporting to Excel
        
            Parameters
            ----------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
            CT_dict : Dict
                Dictionary of all compound type abbreviations in use and their associated expansions
            sinfo : Dict
                Dictionary containing sample information.
                
            Returns
            -------
            BreakdownDF : DataFrame
                Dataframe containing columns associated with matched FID and MS peak data.
        
            """
            
            #Get the total mass of product from the breakdown dataframe
            m_total = np.nansum(BreakdownDF['Mass (mg)'])
            
            #Iterate through every species in the breakdown dataframe and add entries in two new columns: Compound Type and Carbon Number
            for i, row in BreakdownDF.iterrows():
                #If there exists a formula..
                try:
                    #Set breakdown compound type according to the abbreviation already in the breakdown dataframe
                    BreakdownDF.at[i,'Compound Type'] = CT_dict[BreakdownDF.at[i,'Compound Type Abbreviation']]
                    #Obtain a dictionary containing key:value pairs as element:count using the formula string for the ith row
                    chemFormDict = ChemFormula(row['Formula']).element
                    #Use the carbon entry from the above dictionary to assign a carbon number to the ith row
                    BreakdownDF.at[i,'Carbon Number'] = chemFormDict['C']
                #Otherwise, pass
                except:
                    pass
            
            #Get maximum carbon number in breakdown dataframe
            CN_max = int(BreakdownDF['Carbon Number'].max())
        
            #Create a dataframe for saving quantitative results organized by compound type
            CT_DF = pd.DataFrame({'Compound Type':['Aromatics','Linear Alkanes','Branched Alkanes',
                                                        'Cycloalkanes','Alkenes/Alkynes','Other'],
                                        'Mass (mg)':np.empty(6),
                                        'Mass fraction':np.empty(6)})
            
            #Create a dataframe for saving quantitative results organized by carbon number
            CN_DF = pd.DataFrame({'Carbon Number':range(1,CN_max+1,1),
                                        'Mass (mg)':np.empty(CN_max)})
            
            #Create a dataframe for saving quantitative results organized by both compound type and carbon number
            CTCN_DF = pd.DataFrame({'Aromatics': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Linear Alkanes': pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Branched Alkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Cycloalkanes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Alkenes/Alkynes':pd.Series(np.empty(CN_max),index=range(CN_max)),
                                    'Other':pd.Series(np.empty(CN_max),index=range(CN_max))})
            
            #Iterate through every compound type in the compound type dataframe, summing the total respective masses from the breakdown dataframe
            for i, row in CT_DF.iterrows():
                
                #Define a temporary dataframe which contains all rows matching the ith compound type
                tempDF = BreakdownDF.loc[BreakdownDF['Compound Type'] == row['Compound Type']]
                #Assign the ith compound type's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                CT_DF.at[i,'Mass (mg)'] = np.nansum(tempDF['Mass (mg)'])
                #Calculate and assign the ith compound type's mass fraction usingthe total mass from earlier
                CT_DF.at[i,'Mass fraction'] = CT_DF.at[i,'Mass (mg)']/m_total
            
            #Iterate through every carbon number in the carbon number dataframe, summing the total respective masses from the breakdown dataframe
            for i, row in CN_DF.iterrows():
                
                #Define a temporary dataframe which contains all rows matching the ith carbon number
                tempDF = BreakdownDF.loc[BreakdownDF['Carbon Number'] == row['Carbon Number']]
                #Assign the ith carbon number's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                CN_DF.at[i,'Mass (mg)'] = np.nansum(tempDF['Mass (mg)'])
            
            #Iterate through the entire dataframe, getting masses for every compound type - carbon number pair
            for i, row in CTCN_DF.iterrows():
                
                #For every entry in row
                for j in row.index:
                    
                    #Define a temporary dataframe which contains all rows matching the ith carbon number and compound type
                    tempDF = BreakdownDF.loc[(BreakdownDF['Carbon Number'] == i+1) & (BreakdownDF['Compound Type'] == j)]
                    #Assign the ith carbon number/jth compound type's mass as the sum of the temporary dataframe's m_i column, treating nan as zero
                    CTCN_DF.loc[i,j] = np.nansum(tempDF['Mass (mg)'])
                    
                    
            #Get total masses from CT, CN, and CTCN dataframes
            CT_mass = np.nansum(CT_DF['Mass (mg)'])
            CN_mass = np.nansum(CN_DF['Mass (mg)'])
            CTCN_mass = np.nansum(CTCN_DF)
            
            #Create total mass dataframe
            mass_DF = pd.DataFrame({'Total mass source':['Overall breakdown','Compound Type Breakdown','Carbon Number Breakdown','Compound Type + Carbon Number Breakdown'],'Mass (mg)':[m_total,CT_mass,CN_mass,CTCN_mass]})
            
            return BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF
        
        #Unpack compound type and carbon number dictionaries from list
        CL_Dict, CT_Dict = Label_info
        
        #Filter dataframe to remove compounds that do not contain carbon
        BreakdownDF = BreakdownDF.drop(BreakdownDF[[not i for i in BreakdownDF['Formula'].str.contains('C')]].index)
        #Reset the dataframe index
        BreakdownDF.reset_index()
        
        #Run response factor assignment function
        BreakdownDF = assignRF(BreakdownDF, DBRF)
        #Run gas quantification function
        BreakdownDF = gasQuant(BreakdownDF,DBRF,sinfo,total_volume,cutoff)
        #Run further breakdown function
        BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF = moreBreakdown(BreakdownDF, CT_Dict, sinfo)
        
        return BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF

    #Define function that inserts a column to a CTCN Dataframe labeling the carbon number
    def insertCN(CTCN_DF):
        
        #Get the length of the dataframe, take this to be the maximum carbon number
        CN_max = len(CTCN_DF)
        
        #Get a list of carbon numbers for each row
        CN_list = [i for i in range(1,CN_max+1)]
        
        #Insert this list as a new column at the beginning of the dataframe
        CTCN_DF.insert(loc=0, column='Carbon Number', value=CN_list)

        return CTCN_DF
        
    """ DATA IMPORTS """
    print("[AutoQuantification] Importing data...")
    #Import sample information from json file
    with open(os.path.join(DF_Dir,sname,sname+'_INFO.json')) as sinfo_f:
        sinfo = json.load(sinfo_f)

    #Change ISO date-time strings into datetime objects
    sinfo['Start Time'] = datetime.fromisoformat(sinfo['Start Time'])
    sinfo['End Time'] = datetime.fromisoformat(sinfo['End Time'])

    #Calculate a reaction time using the start, end, and heat time values and add to sinfo
    sinfo['Reaction Time'] = abs(sinfo['End Time']-sinfo['Start Time']).total_seconds()/3600 - sinfo['Heat Time']

    #Dictionary of substrings to add to sample name to create file names
    sub_Dict = {'Gas TCD+FID':['_GS2_TCD_CSO.csv'],
                'Gas Labelled MS Peaks':['_GS1_UA_Comp_UPP.csv'],
                'Gas FID+MS':['_GS2_FIDpMS.csv'],
                'Liquid FID':['_LQ1_FID_CSO.csv'],
                'Liquid Labelled MS Peaks':['_LQ1_UA_Comp_UPP'],
                'Liquid FID+MS':['_LQ1_FIDpMS.csv']}

    #Use sample name to form file names using sub_Dict and append full pathnames for all entries
    for key in sub_Dict:
        sub_Dict[key] = [sub_Dict[key][0],os.path.join(DFR_Dir,sname+sub_Dict[key][0])]


    #If the run liquid analysis Boolean is True..
    if lgTF[0]:
        #DEFINE DIRECTORIES FOR LIQUID FID QUANTIFICATION
        #Define directory for liquid matched MS and FID peaks
        DIR_LQ1_FIDpMS = sub_Dict['Liquid FID+MS'][1]
        #Define directory for liquid response factors
        DIR_LQRF = os.path.join(RF_Dir,LRF_file)
        
        #Read matched peak data between liquid FID and MS
        LQ1_FIDpMS = pd.read_csv(DIR_LQ1_FIDpMS)
        
        #Filter FIDpMS to only include rows with non-NaN compounds
        LQ1_FIDpMS_Filtered = LQ1_FIDpMS[LQ1_FIDpMS['Compound Name'].notnull()].reset_index(drop=True)
        
        #Create a duplicate of the FIDpMS dataframe for future saving as a breakdown
        LQ_FID_BreakdownDF = LQ1_FIDpMS_Filtered.copy()
        
        #Read liquid response factors data
        LQRF = {i:pd.read_excel(DIR_LQRF,sheet_name=i) for i in CL_Dict.keys()}
    else:
        pass

    #If the run gas analysis Boolean is True..
    if lgTF[1]:
        #DEFINE DIRECTORIES FOR GAS TCD AND FID QUANTIFICATION
        #Define directory for gas TCD peaks
        DIR_GS2_TCD = sub_Dict['Gas TCD+FID'][1]
        #Define directory for gas FID peaks
        DIR_GS2_FIDpMS = sub_Dict['Gas FID+MS'][1]
        #Define directory for gas TCD response factors
        DIR_TCDRF = os.path.join(RF_Dir,GRFT_file)
        #Define directory for gas FID response factors
        DIR_FIDRF = os.path.join(RF_Dir,GRF_file)
        
        #Read gas FID and TCD Peak data
        GS2_TCD = pd.read_csv(DIR_GS2_TCD)
        
        #Create a duplicate of the gas TCD/FID dataframe for future saving as a breakdown
        #Also filter breakdown dataframe to only include rows sourced from TCD
        GS_TCD_BreakdownDF = GS2_TCD.loc[GS2_TCD['Signal Name'] == 'TCD2B'].copy()
        
        #Read matched peak data between gas FID and MS
        GS2_FIDpMS = pd.read_csv(DIR_GS2_FIDpMS)
        
        #Create a duplicate of the FIDpMS dataframe for future saving as a breakdown
        GS_FID_BreakdownDF = GS2_FIDpMS.copy()
        
        #Read gas TCD response factors data
        TCDRF = pd.read_csv(DIR_TCDRF)
        #Read gas FID response factors data
        GSRF = pd.read_csv(DIR_FIDRF)
        
    else:
        pass

    """ MAIN SCRIPT """

    #If the run liquid analysis Boolean is True..
    if lgTF[0]:
        print("[AutoQuantification] Analyzing liquids...")
        #Get liquid FID breakdown and miscellaneous dataframes
        LQ_FID_BreakdownDF, LQCT_DF, LQCN_DF, LQCTCN_DF, LQmass_DF = liquidFID(LQ_FID_BreakdownDF, LQRF, [CL_Dict, CT_Dict], sinfo)
        
        #Insert the carbon number column to LQCTCN_DF
        LQCTCN_DF = insertCN(LQCTCN_DF)
        
    #If the run gas analysis Boolean is True..
    if lgTF[1]:
        print("[AutoQuantification] Analyzing gases...")
        #If the external standard Boolean is True..
        if ES_bool:
            #Get gas TCD breakdown and miscellaneous dataframes
            GS_TCD_BreakdownDF, TCDRF, total_volume, TCD_cond = gasTCD_ES(GS_TCD_BreakdownDF,TCDRF,sinfo,[gasBag_temp,gasBag_pressure],peak_error)
            
            #Get gas FID breakdown and miscellaneous dataframes
            GS_FID_BreakdownDF, GSCT_DF, GSCN_DF, GSCTCN_DF, GSmass_DF = gasFID_ES(GS_FID_BreakdownDF,GSRF,[CL_Dict, CT_Dict], sinfo,[gasBag_temp,gasBag_pressure],total_volume)
        #Otherwise..
        else:
            #Get gas TCD breakdown and miscellaneous dataframes
            GS_TCD_BreakdownDF, TCDRF, TCD_cond = gasTCD(GS_TCD_BreakdownDF,TCDRF,sinfo,peak_error)
            
            #Get gas FID breakdown and miscellaneous dataframes
            GS_FID_BreakdownDF, GSCT_DF, GSCN_DF, GSCTCN_DF, GSmass_DF = gasFID(GS_FID_BreakdownDF,GSRF,[CL_Dict, CT_Dict], sinfo)
        
        #Insert the carbon number column to GSCTCN_DF
        GSCTCN_DF = insertCN(GSCTCN_DF)

    #If both the gas and liquid analysis Booleans are True..
    if lgTF[0] and lgTF[1]:
        print("[AutoQuantification] Totaling contributions from liquid and gas phases...")
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
        total_CTCN_DF = insertCN(total_CTCN_DF)
        
    #Otherwise, pass
    else:
        pass

    """ BREAKDOWN SAVING """
    print("[AutoQuantification] Formatting and saving breakdown file...")
    #If breakdown directory does not exist within sample folder, create it
    if not os.path.exists(DFbreak_Dir):
        os.makedirs(DFbreak_Dir)
        
    #Define breakdown file name
    bfn = sname+"_Breakdown_"+nows+".xlsx"

    #Create pandas Excel writers
    writer = pd.ExcelWriter(fileCheck(os.path.join(DFbreak_Dir,bfn)), engine="xlsxwriter")

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

    #Log that a new Excel breakdown has been saved
    logger.info("New breakdown created: " + bfn)
    
    print("[AutoQuantification] Matching complete.")
    #Close main function by returning
    return None
