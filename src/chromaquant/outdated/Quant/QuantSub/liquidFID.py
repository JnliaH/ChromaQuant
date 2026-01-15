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

SUBPACKAGE FOR PERFORMING LIQUID QUANTIFICATION STEPS

Julia Hancock
Started 12-29-2024

"""
""" PACKAGES """
import pandas as pd
import math
import numpy as np
from chemformula import ChemFormula

""" FUNCTION """
#Function for quantifying liquid FID data
def liquidFID(BreakdownDF,DBRF,Label_info,sinfo):
    
    #Unpack compound type and carbon number dictionaries from list
    CL_Dict, CT_Dict = Label_info
    
    """ FUNCTIONS """
    #Function to assign compound type and carbon number to compound using formula
    def assignCTCN(BreakdownDF,CT_dict):
        #Iterate through every species in the breakdown dataframe and add entries in two new columns: Compound Type and Carbon Number
        for i, row in BreakdownDF.iterrows():
            #If there exists a formula.. #FIND ALTERNATIVE BESIDES TRY
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