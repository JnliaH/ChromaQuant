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

#Function for quantifying gas TCD data w/ volume estimation method, no pressure adjustment
def gasTCD_VE(BreakdownDF,DBRF,gasBag_cond,peak_error):
    
    #Unpack gas bag conditions
    temp = gasBag_cond[0]       #temperature of gas bag, C
    pressure = gasBag_cond[1]   #sample pressure in gas bag, psi
    co2 = gasBag_cond[2]        #CO2 volume, mL

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
    
    #Convert sinfo variables to new units
    co2 = co2 / 10**6                     #volume injected CO2, m^3
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
    
    return BreakdownDF, volume

#Function for quantifying gas TCD data w/ scale factor method
def gasTCD_SF(BreakdownDF,DBRF,gasBag_cond,reactor_cond,peak_error):
    
    #Initialize compound name column in BreakdownDF
    BreakdownDF['Compound Name'] = 'None'
    
    #Function to determine total volume using ideal gas law
    def volumeIGL(V_C,reactor_cond):

        #Unpack reactor conditions
        P_f = reactor_cond[0]       #reactor quench pressure, psig
        V_R = reactor_cond[1]       #reactor internal volume, mL
        P_0 = reactor_cond[2]       #atmospheric pressure, psi

        #Estimate total volum of gas bag, mL
        V_T = V_R * (P_f + P_0) / P_0

        #Estimate total volume of gas bag plus volume CO2, mL
        V_TC = V_T + V_C

        return V_T, V_TC

    # Function to estimate scale factor from CO2
    def getScaleFactor(BreakdownDF,DBRF,V_C,V_TC):

        #Find the CO2 peak row in DBRF
        CO2_row = DBRF.loc[DBRF['Compound Name'] == "Carbon Dioxide"].iloc[0]
        
        #Get the retention time
        CO2_RT = CO2_row['RT (min)']
        
        #Get the minimum and maximum of the RT range using the peak error
        CO2_RTmin = CO2_RT - peak_error
        CO2_RTmax = CO2_RT + peak_error
        
        #Define boolean describing whether or not CO2 match has been found
        CO2_bool = False

        #Iterate through every row in BreakdownDF
        for i, row in BreakdownDF.iterrows():
            
            #If the TCD retention time is within range of the CO2 entry...
            if CO2_RTmin <= row['RT'] <= CO2_RTmax:
                
                #Get estimated volume fraction of CO2
                psiCO2_e = row['Area'] / (100 * CO2_row['RF'])

                #Get actual volume fraction of CO2
                psiCO2_a = V_C / V_TC

                #Define scale factor as ratio of actual volume fraction to estimated volume fraction
                SF = psiCO2_a / psiCO2_e

                #Set CO2_bool to True
                CO2_bool = True
                
                break
            
            #Otherwise, pass
            else:
                pass

        #Raise error if no CO2 peak found
        if CO2_bool == False:
            raise Exception("[gasTCD][ERROR] No CO2 peak found in TCD")

        else:
            pass

        return SF

    #Function to calculate amounts of each species using the scale factor
    def quantTCD(BreakdownDF,DBRF,gasBag_cond,reactor_cond):

        # Unpack gas bag conditions
        GB_temp = gasBag_cond[0]       # Temperature of gas bag, C
        GB_pressure = gasBag_cond[1]   # Sample pressure in gas bag, psig
        V_C = gasBag_cond[2]           # CO2 volume, mL

        # Get total and total+CO2 gas bag volumes
        V_T, V_TC = volumeIGL(V_C,reactor_cond)

        # Define ideal gas constant, m^3*Pa/K*mol
        R = 8.314

        #Define conversion factor, Pa * m^3 * psi^-1 * mL^-1
        C = 0.00689476

        #Get scale factor
        SF = getScaleFactor(BreakdownDF,DBRF,V_C,V_TC)

        #Add min and max peak assignment values to DBRF
        for i, row in DBRF.iterrows():
            DBRF.at[i,'RT Max'] = DBRF.at[i,'RT (min)'] + peak_error
            DBRF.at[i,'RT Min'] = DBRF.at[i,'RT (min)'] - peak_error

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
                    
                    #Get estimated volume percent using response factor
                    volpercent_e = row['Area']/row2['RF']
                    BreakdownDF.at[i,'Est. Vol.%'] = volpercent_e

                    #Get adjusted volume percent using scale factor
                    volpercent_a = volpercent_e * SF
                    BreakdownDF.at[i,'Adj. Vol.%'] = volpercent_a
                    
                    #Get moles using ideal gas law (PV=nRT)
                    BreakdownDF.at[i,'Moles (mol)'] = C * (GB_pressure * volpercent_a * V_TC)/(R * (GB_temp + 273.15))
                    
                    #Get mass (mg) using moles and molar mass
                    BreakdownDF.at[i,'Mass (mg)'] = BreakdownDF.at[i,'Moles (mol)'] * BreakdownDF.at[i,'MW (g/mol)'] * 1000
                
                #Otherwise, pass    
                else:
                    pass
        
        return BreakdownDF, V_TC, SF
    
    BreakdownDF, V_TC, SF = quantTCD(BreakdownDF,DBRF,gasBag_cond,reactor_cond)
    
    return BreakdownDF, V_TC, SF

#Function for quantifying gas TCD data w/ internal standard method
def gasTCD_IS(BreakdownDF,DBRF,gasBag_cond,peak_error):
    
    #Unpack gas bag conditions
    temp = gasBag_cond[0]       #temperature of gas bag, C
    pressure = gasBag_cond[1]   #sample pressure in gas bag, psi
    co2 = gasBag_cond[2]        #CO2 volume, mL

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
    
    #Convert sinfo variables to new units
    co2 = co2 / 10**6                     #volume injected CO2, m^3
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
    
    return BreakdownDF, volume