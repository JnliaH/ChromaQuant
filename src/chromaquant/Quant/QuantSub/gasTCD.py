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

SUBPACKAGE FOR PERFORMING GAS TCD QUANTIFICATION STEPS

Julia Hancock
Started 12-29-2024

"""
""" PACKAGES """
from chemformula import ChemFormula

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