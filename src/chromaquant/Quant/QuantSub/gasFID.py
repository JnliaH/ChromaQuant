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

SUBPACKAGE FOR PERFORMING GAS FID QUANTIFICATION STEPS

Julia Hancock
Started 12-29-2024

"""
""" PACKAGES """
import pandas as pd
import numpy as np
from chemformula import ChemFormula

#Function for quantifying gas FID data w/ external standard
def gasFID_ES(BreakdownDF,DBRF,Label_info,gasBag_cond,total_volume,cutoff=4):
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
    gasBag_cond : List
        List containing gas bag temperature [0] and gas bag pressure [1]
    Label_info : List
        List of dictionaries containing chemical lump and compound type abbreviations
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
    def gasQuant(BreakdownDF,DBRF,total_volume,cutoff):
        
        #Remove rows in BreakdownDF with a carbon number at or below cutoff
        BreakdownDF = BreakdownDF.loc[BreakdownDF['Carbon Number'] > cutoff].copy()
        
        #Get gas bag conditions
        temp = gasBag_cond[0]       #temperature of gas bag, C
        pressure = gasBag_cond[1]   #sample pressure in gas bag, psi
        
        #Convert gas bag conditions to new units
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
    def moreBreakdown(BreakdownDF,CT_dict):
        """
        This function prepares further breakdown dictionaries for use in exporting to Excel
    
        Parameters
        ----------
        BreakdownDF : DataFrame
            Dataframe containing columns associated with matched FID and MS peak data.
        CT_dict : Dict
            Dictionary of all compound type abbreviations in use and their associated expansions
            
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
    BreakdownDF = gasQuant(BreakdownDF,DBRF,total_volume,cutoff)
    #Run further breakdown function
    BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF = moreBreakdown(BreakdownDF, CT_Dict)
    
    return BreakdownDF, CT_DF, CN_DF, CTCN_DF, mass_DF