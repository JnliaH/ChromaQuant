#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

SCRIPT THAT TAKES MATCHED FID AND MS PEAKS AND ASSESSES DUPLICATES
Julia Hancock

Started 7-26-2024

"""

""" PACKAGES """

import sys
import pandas as pd
import os

""" SAMPLE INFO """
#Sample name
sname = 'example2'

#Sample phase
phase = 'L'

""" DIRECTORIES """

#Get current working directory
cwd = os.path.dirname(__file__)

#Set up dictionary containing all relevant directories
direcDict = {'cwd':cwd,                                   #Main directory
             'resources':cwd+'/resources/',               #Resources directory
             'DF_Dir':cwd+"/data/"+sname+"/",             #Data files directory
             'DF_raw':cwd+"/data/"+sname+"/raw data/",    #Raw data files directory
             'DFlog_Dir':cwd+"/data/"+sname+"/log/"}      #Data file log directory

#Dictionary of substrings to add to sample name to create file names
sub_Dict = {'Gas TCD+FID':['_GS2_TCD_CSO.csv'],
            'Gas Labelled MS Peaks':['_GS1_UA_Comp_UPP.csv'],
            'Gas FID+MS':['_GS2_FIDpMS.csv'],
            'Liquid FID':['_LQ1_FID_CSO.csv'],
            'Liquid Labelled MS Peaks':['_LQ1_UA_Comp_UPP.csv'],
            'Liquid FID+MS':['_LQ1_FIDpMS.csv'],
            'Info':['_INFO.json']}


""" FUNCTIONS """

#Define function that loops through every row and modifies rows with duplicate compounds
def duplicateHandle(DF):
    
    #Define function that searches for rows in a DataFrame with duplicate compound names
    def duplicateSearch(DF,cmp_name):
        
        #Get a new dataframe that is a copy of the first argument
        DF_out = DF.copy()
        
        #Filter the dataframe using the provided compound name
        DF_out = DF_out[DF_out['Compound Name'] == cmp_name]
        
        #Define a Boolean describing whether or not there are duplicate rows
        duplicate_TF = False
        
        #If the DF_out dataframe is longer than one (if there are duplicate rows)...
        if len(DF_out) > 1:
            
            #Assign the Boolean to true
            duplicate_TF = True
            
            #Define the dataframe to be returned
            DF_return = DF_out.copy()
            
        #Otherwise, define the return dataframe as empty
        else:
            DF_return = pd.DataFrame
            
        #Return the boolean and the filtered DataFrame
        return duplicate_TF, DF_return
    
    #Define function that handles a given DataFrame of duplicates
    def duplicateLogic(DF_search):
        
        #Define the output DataFrame as an in copy
        DF_logic = DF_search.copy()
        
        #Get the row in the DataFrame with the largest area
        maxSeries = DF_logic.loc[DF_logic['FID Area'].idxmax()]
        
        #Get the name and compound type of this compound
        max_name = maxSeries['Compound Name']
        max_type = maxSeries['Compound Type Abbreviation']
        
        #Get the remaining entries in the DataFrame
        DF_logic = DF_logic.drop([maxSeries.name],axis=0)
        
        #For every row in the remaining entries DataFrame, rename the compound to 'Isomer of..' 
        for i, row in DF_logic.iterrows():
            
            #Get the new compound name
            new_cmp_name = 'Isomer of ' + max_name
            
            #Replace the compound name
            DF_logic.at[i,'Compound Name'] = new_cmp_name
            
            #If the compound type of the maxSeries is linear alkanes...
            if max_type == 'L':
                
                #Set the current row's compound type to branched alkanes
                DF_logic.at[i,'Compound Type Abbreviation'] = 'B'
                
            #Otherwise, pass
            else:
                pass
        
        #Return the logic DataFrame
        return DF_logic
    
    #Define a function that replaces rows in the primary DataFrame with matches in the secondary, assuming the indices match
    def duplicateReplace(pDF,sDF):
        
        #For every entry in the secondary DataFrame...
        for i, row in sDF.iterrows():
            
            #Get the row's name, which is the numeric index in the DataFrame
            row_name = row.name
            
            #For every index in the row...
            for j in row.index:
                
                #Replace the corresponding entry in the pDF at the preserved sDF index
                pDF.at[row_name,j] = row[j]
        
        return pDF
        
    #Define a list of compound names already handled
    cmp_nameList = []
    
    #Create a copy of the argument DataFrame to be used
    DF_in = DF.copy()
    
    #Initiate a DataFrame for the logic output
    DF_logic = pd.DataFrame()
    
    #For every row in the provided DataFrame
    for i, row in DF_in.iterrows():
        
        #Get the compound name in that row
        cmp_name = row['Compound Name']
        
        #If the compound name is in the list of compound names handled, pass
        if cmp_name in cmp_nameList:
            pass
        
        #Otherwise...
        else:
                
            #If the compound name is 'No Match' or 'No match' or nan, pass
            if cmp_name == 'No Match' or cmp_name == 'No Match' or pd.isna(cmp_name):
                pass
            
            #Otherwise...
            else:
                
                #Run the duplicate search function for that compound name
                duplicate_TF, DF_search = duplicateSearch(DF_in,cmp_name)
                
                #If duplicate_TF is True...
                if duplicate_TF:
                    #Run the duplicate logic funcion
                    DF_logic = duplicateLogic(DF_search)
                    
                    #Run the duplicate replace function
                    DF_done = duplicateReplace(DF_in,DF_logic)
                    
                #Otherwise, pass
                else:
                    pass
                
                #Add the compound name to the compound name list
                cmp_nameList.append(cmp_name)
        
    return DF_done
    
    
""" CODE """

#Get dataframe containing FID and MS matches
DF = pd.read_csv(direcDict['DF_raw']+sname+sub_Dict['Liquid FID+MS'][0])

#Run the compound search function
DF_done = duplicateHandle(DF)

cmp_name = '6,6-Dimethylhepta-2,4-diene'






