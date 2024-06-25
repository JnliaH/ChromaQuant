
"""

SCRIPT TO QUANTIFY COMPOUNDS IN SAMPLE USING DEFINED RESPONSE FACTORS

Julia Hancock
Started 12/14/2023

"""
""" NEXT STEPS """
#1. Verify that response factors are being read and assigned correctly according to intended logic

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

""" SAMPLE INFO """
#Get list of system arguments
argList = sys.argv

#Get sample name
sname = argList[1]

#Get sample phase ("L" or "G")
quantphases = argList[2]

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

#Start time for execution time
exec_start = datetime.now()

""" DIRECTORIES """

#Main directory
cwd = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/Quantification/"
#Data files directory
DF_Dir = cwd+"data/"+sname+"/"
#Response factors directory
RF_Dir = cwd+"response-factors/"
#Resources directory
RE_Dir = cwd+"resources/"
#Data file log directory
DFlog_Dir = DF_Dir+"log/"
#Data file breakdowns directory
DFbreak_Dir = DF_Dir+"breakdowns/"

""" LOGGING """
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
fh = logging.FileHandler(DFlog_Dir+'quantlog_'+nows+'.log')
logger.addHandler(fh)
logger.propagate = False
#Set logging level
logger.setLevel(logging.INFO)
#Create a formatter and assign to logger
formatter = logging.Formatter('[%(filename)s] %(asctime)s - [%(levelname)s]: %(message)s')
fh.setFormatter(formatter)


""" LABELS """

#Dictionary of all chemical lump abbreviations in use and their associated expansions
CL_Dict = {'MBE':'Methyl benzenes', 'ABE':'Alkyl benzenes', 'NAP':'Napthalenes', 'MAL':'Methl alkanes',
           'DAL':'Dimethyl alkanes','TAL':'Trimethyl alkanes','MCA':'Methyl cycloalkanes','ACA':'Alkyl cycloalkanes',
           'AAL':'Alkyl alkanes','MAE':'Methyl alkenes','DAE':'Dimethyl alkenes','AAE':'Alkyl alkenes',
           'LAL':'Linear alkanes','CAE':'Cycloalkenes','IND':'Indenes','PAH':'Polycyclic aromatic hydrocarbons',
           'AKY':'Alkynes'}

#Alphabetize lump abbreviation dictionary
CL_Dict = dict(sorted(CL_Dict.items()))

#Dictionary of all compound type abbreviations in use and their associated expansions
CT_Dict = {'A':'Aromatics','L':'Linear Alkanes','B':'Branched Alkanes',
           'C':'Cycloalkanes','E':'Alkenes/Alkynes','O':'Other'}

#Alphabetize compound type abbreviation dictionary
CT_Dict = dict(sorted(CT_Dict.items()))

""" FUNCTIONS """

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
    
        #Loop through every labelled peak in the filtered FIDpMS dictionary
        for i, row in BreakdownDF.iterrows():
            #Find the compound name
            cmp_name = row['Compound Name']
            
            #Loop through every sheet in the liquid response factors dataframe
            for CLkey in DBRF:
                
                #If the compound name is in a given sheet..
                if cmp_name in DBRF[CLkey]['Compound Name'].values:
                    
                    #Get the index where it is listed
                    cmp_index = DBRF[CLkey].index[DBRF[CLkey]['Compound Name'] == cmp_name]
                    
                    #Assign the listed response factor in the matched sheet to the RF variable
                    RF = DBRF[CLkey].loc[cmp_index,'Response Factor'].iloc[0]
                    
                    #If RF is nan..
                    if math.isnan(RF):
                        
                        #If the estimated response factor in that row is nan..
                        if math.isnan(DBRF[CLkey].loc[cmp_index,'Estimated Response Factor'].iloc[0]):
                            #Set RF to 1
                            RF = 1
                            #Set the value for response factor in the breakdown dataframe to RF
                            BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                            #Set the RF source to "Assumed 1, could not find an empirical or extrapolated response factor"
                            BreakdownDF.at[i,'RF Source'] = 'Assumed 1, compound in RF database but lacks any RF'
                            break
                        
                        #Otherwise..
                        else:
                            
                            #If the estimated response factor is negative or larger than 5, set RF to 1
                            if DBRF[CLkey].loc[cmp_index,'Estimated Response Factor'].iloc[0] < 0 or DBRF[CLkey].loc[cmp_index,'Estimated Response Factor'].iloc[0] > 5:
                                RF = 1
                                #Set the value for response factor in the breakdown dataframe to RF
                                BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                                #Set the RF source to "Assumed 1, estimated response factor exists but is out of range"
                                BreakdownDF.at[i,'RF Source'] = 'Assumed 1, estimated response factor exists but is out of range'
                                
                            #Otherwise, set RF to the estimated response factor
                            else:
                                #Set RF to the estimated response factor
                                RF = DBRF[CLkey].loc[cmp_index,'Estimated Response Factor'].iloc[0]
                                #Set the value for response factor in the breakdown dataframe to RF
                                BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                                #Set the RF source to "Estimated response factor in chemical lump"
                                BreakdownDF.at[i,'RF Source'] = 'Estimated response factor in chemical lump ' + CLkey
                            
                            
                            break
                    
                    #Otherwise..
                    else:
                        #Set the value for response factor in the breakdown dataframe to RF
                        BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                        #Set the RF source to "Empirical response factor"
                        BreakdownDF.at[i,'RF Source'] = 'Empirical response factor'
                        break
                else:
                    if CLkey != list(CL_Dict.keys())[-1]:
                        pass
                    else:
                        #Set RF to 1
                        RF = 1
                        #Set the value for response factor in the breakdown dataframe to RF
                        BreakdownDF.at[i,'Response Factor ((A_i/A_T)/(m_i/m_T))'] = RF
                        #Set the RF source to "Assumed 1, could not find compound in RF database"
                        BreakdownDF.at[i,'RF Source'] = 'Assumed 1, could not find compound in RF database'
                        break
        
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

    #Use the assignRF function to assign response factors, preferring empirical RF's to estimated ones and assigning 1 when no other RF can be applied
    BreakdownDF = assignRF(BreakdownDF,DBRF,CL_Dict)

    #Use the quantMain function to add quantitative data to BreakdownDF
    BreakdownDF = quantMain(BreakdownDF,sinfo)

    #Use the moreBreakdown function to prepare compound type and carbon number breakdowns
    BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF = moreBreakdown(BreakdownDF,CT_Dict,sinfo)
    
    return [BreakdownDF,CT_DF,CN_DF,CTCN_DF, mass_DF]

#Function for quantifying gas TCD data
def gasTCD(BreakdownDF,DBRF,sinfo):
    #Define retention time error within which peaks may be assigned
    peak_error = 0.5
    
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

#Function for quantifying gas FID data
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
    cutoff : , optional
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


""" DATA IMPORTS """
#Import sample information from json file
with open(DF_Dir+sname+'_INFO.json') as sinfo_f:
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
    sub_Dict[key] = [sub_Dict[key][0],DF_Dir+sname+sub_Dict[key][0]]


#If the run liquid analysis Boolean is True..
if lgTF[0]:
    #DEFINE DIRECTORIES FOR LIQUID FID QUANTIFICATION
    #Define directory for liquid matched MS and FID peaks
    DIR_LQ1_FIDpMS = sub_Dict['Liquid FID+MS'][1]
    #Define directory for liquid response factors
    DIR_LQRF = RF_Dir+"Liquid Response Factors.xlsx"
    
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
    DIR_TCDRF = RF_Dir+"TCDRF.csv"
    #Define directory for gas FID response factors
    DIR_FIDRF = RF_Dir+"gasFIDRF.csv"
    
    #Read gas FID and TCD Peak data
    GS2_TCD = pd.read_csv(DIR_GS2_TCD)
    
    #Create a duplicate of the gas TCD/FID dataframe for future saving as a breakdown
    #Also filter breakdown dataframe to only include rows sourced from TCD
    GS_TCD_BreakdownDF = GS2_TCD.loc[GS2_TCD['Signal Name'] == 'TCD2B'].copy()
    
    #Read matched peak data between gas FID and MS
    GS2_FIDpMS = pd.read_csv(DIR_GS2_FIDpMS)
    
    #Filter FIDpMS to only include rows with non-NaN MS retention times
    GS2_FIDpMS_Filtered = GS2_FIDpMS[GS2_FIDpMS['MS RT'].notnull()].reset_index(drop=True)
    
    #Create a duplicate of the FIDpMS dataframe for future saving as a breakdown
    GS_FID_BreakdownDF = GS2_FIDpMS_Filtered.copy()
    
    #Read gas TCD response factors data
    TCDRF = pd.read_csv(DIR_TCDRF)
    #Read gas FID response factors data
    GSRF = pd.read_csv(DIR_FIDRF)
else:
    pass

""" MAIN SCRIPT """

#If the run liquid analysis Boolean is True..
if lgTF[0]:
    #Get liquid FID breakdown and miscellaneous dataframes
    LQ_FID_BreakdownDF, LQCT_DF, LQCN_DF, LQCNCT_DF, LQmass_DF = liquidFID(LQ_FID_BreakdownDF, LQRF, [CL_Dict, CT_Dict], sinfo)
else:
    pass

#If the run gas analysis Boolean is True..
if lgTF[1]:
    #Get gas TCD breakdown and miscellaneous dataframes
    GS_TCD_BreakdownDF, TCDRF, TCD_cond = gasTCD(GS_TCD_BreakdownDF,TCDRF,sinfo)
    
    #Get gas FID breakdown and miscellaneous dataframes
    GS_FID_BreakdownDF, GSCT_DF, GSCN_DF, GSCNCT_DF, GSmass_DF = gasFID(GS_FID_BreakdownDF,GSRF,[CL_Dict, CT_Dict], sinfo)
else:
    pass

#Get dataframe for sample info
sinfo_DF = pd.DataFrame(sinfo,index=[0])


""" BREAKDOWN SAVING """

#If breakdown directory does not exist within sample folder, create it
if not os.path.exists(DFbreak_Dir):
    os.makedirs(DFbreak_Dir)
    
#Define breakdown file name
bfn = sname+"_Breakdown_"+nows+".xlsx"

#Create pandas Excel writer
writer = pd.ExcelWriter(fileCheck(DFbreak_Dir+bfn), engine="xlsxwriter")

#If the run liquid analysis Boolean is True..
if lgTF[0]:
    #Position the liquid FID dataframes in the worksheet.
    sinfo_DF.to_excel(writer, sheet_name="Liquid FID",startcol=1, startrow=1, index=False) 
    LQ_FID_BreakdownDF.to_excel(writer, sheet_name="Liquid FID",startcol=1, startrow=4, index=False)
    LQCT_DF.to_excel(writer, sheet_name="Liquid FID",startcol=16, startrow=7, index=False)
    LQCN_DF.to_excel(writer, sheet_name="Liquid FID", startcol=16, startrow=15, index=False)
    LQCNCT_DF.to_excel(writer, sheet_name="Liquid FID", startcol=21, startrow=7, index=False)
    LQmass_DF.to_excel(writer, sheet_name="Liquid FID",startcol=20, startrow=1,index=False)
    
else:
    pass

#If the run gas analysis Boolean is True..
if lgTF[1]:
    #Position the gas FID dataframes in the worksheet.
    sinfo_DF.to_excel(writer, sheet_name="Gas FID",startcol=1, startrow=1, index=False) 
    GS_FID_BreakdownDF.to_excel(writer, sheet_name="Gas FID",startcol=1, startrow=4, index=False)
    GSCT_DF.to_excel(writer, sheet_name="Gas FID",startcol=21, startrow=7, index=False)
    GSCN_DF.to_excel(writer, sheet_name="Gas FID", startcol=21, startrow=15, index=False)
    GSCNCT_DF.to_excel(writer, sheet_name="Gas FID", startcol=24, startrow=7, index=False)
    GSmass_DF.to_excel(writer, sheet_name="Gas FID",startcol=21, startrow=1,index=False)
    
    #Expand sample info dataframe to include total TCD mass
    sinfo_DF.at[0,'Total product (mg)'] = GS_TCD_BreakdownDF['Mass (mg)'].sum()
    
    #Position the gas TCD dataframes in the worksheet
    GS_TCD_BreakdownDF.to_excel(writer, sheet_name="Gas TCD",startcol=1,startrow=4, index=False)
    sinfo_DF.to_excel(writer, sheet_name="Gas TCD",startcol=1, startrow=1, index=False) 
else:
    pass

#Close the Excel writer
writer.close()

#Log that a new Excel breakdown has been saved
logger.info("New breakdown created: " + bfn)

#End time for execution time
exec_end = datetime.now()
#Execution time
exec_time = (exec_end-exec_start).total_seconds()*10**3
print("Time to execute: {:.03f}ms".format(exec_time))

""" SAMPLE INFO SAVING"""

"""
x = {'Sample Name':sname,
     'Reactor Name':'MB01',
     'Catalyst Type':'Ru/C+BEA',
     'Catalyst Amount (mg)':59.9,
     'Plastic Type':'PE4k Sigma-Aldrich',
     'Plastic Amount (mg)':299.7,
     'Reaction Temperature (C)':256,
     'Quench Temperature (C)':26,
     'Reaction Pressure (psi)':269,
     'Initial Pressure (psi)':122,
     'Quench Pressure (psi)':27,
     'Start Time':'2023-12-01 13:29:00.000',
     'End Time':'2023-12-04 12:43:00.000',
     'Heat Time':1+17/60,
     'Internal Standard Name':'TTBB',
     'Internal Standard Mass (mg)':13.5}

#Write to JSON
with open(cwd+sname+'_INFO.json','w',encoding='utf-8') as f:
    json.dump(x,f,ensure_ascii=False, indent=4)
"""











