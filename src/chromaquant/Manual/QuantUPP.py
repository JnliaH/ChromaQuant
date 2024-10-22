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

UNKNOWNS ANALYSIS POST PROCESSING
Intended to sort through raw UA output to find best hits considering
compound constraints.

Julia Hancock
08/25/2023

First version (v1) completion: 08/31/2023

Improvement notes: -Add places to throw error and redirect user through console when user-inputted data goes wrong
                   -Add GUI
                   -Separate functions into packages, redesign nested function trees
                   -Check if saving data will cause an overwrite - if it does, add an additional suffix
"""

""" PACKAGES """

import pandas as pd
import numpy as np
import os
from pathlib import Path
import re

""" PARAMETERS """

#DIRECTORIES
#Name of folder to search for files
infolder_name = "MBPR025-033_GasMS_UA_Comp"
#Name of folder to export results
outfolder_name = infolder_name + "_UPP"
#PARAMETERS
#Limit of identical peak RT
PeakRTLim = 0.005

""" DIRECTORIES """

#Find main file' path and its parent directory
main_filepath = Path(__file__)
main_directory = main_filepath.parent
import_directory = main_directory / "Imports"
export_directory = main_directory / "Exports"

#Directory for finding relevant files
fileDir = import_directory / infolder_name
#Directory for exporting constrained data
expfileDir = export_directory / outfolder_name

#Create list of string paths for each file in provided file directory
fileLoc = []
for path, subdirs, files in os.walk(fileDir):
    for name in files:
        fileLoc.append(os.path.join(path, name))

""" COMPOUND CONSTRAINS """
#Establish lists for two levels of element restrictions:
    #1st list (softBar) - elements that will be allowed in compound match if there are no compound matches
    #                     with only allowed elements. When time comes, list will be searched for matches in
    #                     order of priority
    #2nd list (noBar) - elements that will always be allowed

#Class for elements to enable compound constraints
class element:
    def __init__(self, Symbol, Name, Priority=float("nan")):
        #Element must always have symbol and name
        self.Symbol = Symbol
        self.Name = Name
        #Element does not necessarily need priority - this is an integer allowing for more precise
        #control over choosing compound matches
        if Priority == float("nan"):
            pass
        else:
            if isinstance(Priority, int) and Priority > 0:
                self.Priority = Priority
            else:
                pass

#softBar list of semi-allowed elements
#softBar = [element("O","Oxygen",1),element("N","Nitrogen",2),element("Si","Silicon",4)]
softBar = [element("O","Oxygen",1),element("Si","Silicon",4)]
#noBar list of allowed elements
noBar = [element("H","Hydrogen"),element("C","Carbon")]

""" FUNCTIONS """
#Function to unpack .csv file
def unpackUA(filepath):
    Df = pd.read_csv(filepath)
    return Df

#Function to add match data to dataframe
def concatDF(dataSlice, DFin):
    #Assumes a dataframe provided with these columns: ['Component RT','Compound Name','Formula','Match Factor']
    #Also assumes dataSlice will contain at least these same columns
    col = ['Component RT','Compound Name','Formula','Match Factor','Previous Best Compound Name',\
           'Previous Best Formula','Previous Best Match Factor','Previous Worst Compound Name',\
           'Previous Worst Formula','Previous Worst Match Factor']
    listOut = [dataSlice[col[i]] for i in range(len(col))]
    DFout = pd.concat([pd.DataFrame([listOut], columns=DFin.columns), DFin], ignore_index=True)
    
    return DFout

#Function to add series of matches with best and worst match factor to a selected match series
def concatSeries(dataSlice, bestSlice, worstSlice):
    #Assumes all Series have these columns: ['Component RT','Compound Name','Formula','Match Factor']
    
    #Define dictionaries of new index names for bestSlice and worstSlice
    bindex = {'Component RT':'Previous Best Component RT','Compound Name':'Previous Best Compound Name',
                'Formula':'Previous Best Formula','Match Factor':'Previous Best Match Factor'}
    windex = {'Component RT':'Previous Worst Component RT','Compound Name':'Previous Worst Compound Name',
                'Formula':'Previous Worst Formula','Match Factor':'Previous Worst Match Factor'}
    
    #Rename bestSlice and worstSlice indices
    bestSlice = bestSlice.copy()
    worstSlice = worstSlice.copy()
    bestSlice.rename(index=bindex, inplace=True)
    worstSlice.rename(index=windex, inplace=True)
    
    #Lists of indices from best/worst slices we want to add to dataSlice
    bindexList = ['Previous Best Compound Name','Previous Best Formula','Previous Best Match Factor']
    windexList = ['Previous Worst Compound Name','Previous Worst Formula','Previous Worst Match Factor']
    
    #Define returnSeries
    returnSlice = pd.concat([dataSlice,bestSlice.loc[bindexList],worstSlice.loc[windexList]], axis=0)
    return returnSlice

#Function to group retention times, taking median to be value of grouped peaks
def groupRT(rawDF):
    
    #Redefine for clarity
    filterDF = rawDF.copy()
    
    #Set up empty list for output RT (RT_permF), an empty list for temporary (original) RT's
    #(RT_temp) with only the first original RT, and the median of that list
    RT_permF = []
    RT_temp = [rawDF['Component RT'][0]]
    RT_temp_median = RT_temp[0]
    
    #For all raw retention times, group times within the PeakRTLim of each other.
    for i in range(1,len(rawDF['Component RT'])):
        #Current retention time
        RT_current = rawDF['Component RT'][i]

        #If current retention time within the median plus the peak limits, redefine median
        if RT_current < RT_temp_median+PeakRTLim and RT_current > RT_temp_median-PeakRTLim:
            #Append to list of like retention times
            RT_temp.append(RT_current)
            #Recalculate median, rounding to 4 decimal places
            RT_temp_median = round(np.median(RT_temp),4)
            #If it's reached the end of the dataframe, append what's left
            if i == len(rawDF['Component RT']) - 1:
                RT_permF.extend(np.full(len(RT_temp),RT_temp_median))
                RT_temp_median = RT_current
                RT_temp = [RT_current]
        
        #Otherwise, save the RT_temp_median to all RT_temp positions, redefine RT_temp and RT_temp_median
        else:
            #Set old retention times to median
            filterDF.loc[i-len(RT_temp):i, ('Component RT')] = RT_temp_median
            RT_permF.extend(np.full(len(RT_temp),RT_temp_median))
            RT_temp_median = RT_current
            RT_temp = [RT_current]
    
    #Delete/return variables
    del RT_permF, RT_temp, RT_temp_median, RT_current
    return filterDF

#Function to return True if formula only contains noBar restrictions
def donoBar(formula, noBar):
    
    #Find all elements present in formula
    elements = re.findall('[A-Z][a-z]?',formula)
    #Get list of allowed elements from noBar dataframe
    allowed_elements = [noBar[i].Symbol for i in range(len(noBar))]
    
    #..If a set of the difference between the lists is not empty (there are formula elements besides allowed ones), return False
    if set(elements).difference(set(allowed_elements)):
        tf = False
    #..Otherwise, return True
    else:
        tf = True
        
    return tf
    
#Function to return True if formula only contains softBar restrictions of given priority
def dosoftBar(formula,noBar,softBar,priority):
    
    #Find all elements present in formula
    elements = re.findall('[A-Z][a-z]?',formula)
    #Get dataframe of elements and priority from softBar
    ePDF = pd.DataFrame.from_dict({"Symbol":[obj.Symbol for obj in softBar], "Priority":[obj.Priority for obj in softBar]})
    #Get list of symbols with provided priority or lower, add elements from noBar
    allowed_elements = ePDF.loc[ePDF['Priority']<=priority, 'Symbol'].to_list()
    allowed_elements.extend([noBar[i].Symbol for i in range(len(noBar))])
    #Delete elements dataframe
    del ePDF
    
    #..If a set of the difference between the lists is not empty (there are formula elements besides allowed ones), return False
    trial = set(elements).difference(set(allowed_elements))
    if set(elements).difference(set(allowed_elements)):
        tf = False
    #..Otherwise, return True
    else:
        tf = True

    return tf

#Function to choose best matches according to compound constraints
def constrain(filterDF, constList):
    """
    This function loops through the dataframe, selecting the best match out of duplicate retention time matches.
    
    INPUTS:  filterDF - the dataframe to be filtered
             constList - a list containing constraints in the form [noBar, softBar]
            
    OUTPUTS: constDF - a dataframe containing the best matches for each retention time
    
    APPROACH: 1) Get a list of all retention times in the dataframe;
              2) Loop through each retention time, getting a slice of each dataframe;
              3) Loop through compound constraints to pick the best match in the slice;
              4) Append result to new, constrained dataframe
    
    SELECTING BEST MATCH:   1) If first formula of sorted slice contains only noBar, add to constrained dataframe
                            2) Otherwise, test next formula
                            3) If all other formulas have elements besides noBar, go back to first value and 
                               allow its formula if it contains only highest priority elements
                            4) If it contains lower priority/blocklist elements, repeat down slice
                            5) If all formulas contain lower priority elements, allow the next priority and repeat search
                            5) If all formulas contain elements not listed in noBar or softBar, add "No Match" row
    """
    
    #Unpack constList into softBar and hardBar
    noBar, softBar = constList
    #Get list of written priorities from softBar and sort them by descending
    priorList = sorted(list(set([x.Priority for x in softBar])))
    #Get list of all retention times
    arrayRF = filterDF['Component RT'].unique()
    #Create dictionary for outputted data
    constDF = pd.DataFrame(columns=['Component RT','Compound Name','Formula','Match Factor','Previous Best Compound Name',\
                                    'Previous Best Formula','Previous Best Match Factor','Previous Worst Compound Name',\
                                    'Previous Worst Formula','Previous Worst Match Factor'])
    
    
    #For every listed retention time, select best match
    for RTi in arrayRF:
        
        #Get a slice containing all possible compounds at given RT
        compound_slice = filterDF.loc[(filterDF["Component RT"] == RTi)]
        #Remove Unknowns from slice, if slice is empty then skip one loop
        compound_slice = compound_slice.loc[~compound_slice["Compound Name"].str.contains("Unknown")]
        #Sort slice by match factor, reset indices
        test_slice = compound_slice.sort_values(by=['Match Factor'], ascending=False).reset_index(drop=True)
        
        #Find rows with best and worst match factors
        try:
            best_match = test_slice.iloc[0,:]
            worst_match = test_slice.iloc[len(test_slice)-1,:]
        except:
            best_match = pd.Series(dtype='float64',index=['Component RT','Compound Name','Formula','Match Factor'])
            worst_match = pd.Series(dtype='float64',index=['Component RT','Compound Name','Formula','Match Factor'])

        #Set search True/False Boolean to True
        search_tf = True
        #Set counted_loops to 0
        counted_loops = 0
        #While loop to continue search function until match is either found or not
        while search_tf == True and counted_loops < 100:
            
            #For every row in the slice sorted by match factor..
            for index, row in test_slice.iterrows():
                #..If the formula meets the noBar criteria, choose row and break formula
                if donoBar(row['Formula'],noBar) and counted_loops == 0:
                    constSeries = concatSeries(row,best_match,worst_match)
                    constDF = concatDF(constSeries,constDF)
                    search_tf = False
                    break
                #..Otherwise if the loop number is greater than 0 and less than the 
                #  number of unique softBar priorities, determine if formula meets softBar criteria
                elif counted_loops > 0 and counted_loops < len(priorList):
                    #Try/except in case the counted loops goes higher than the priority list
                    try:
                        if dosoftBar(row['Formula'],noBar,softBar,priorList[counted_loops-1]):
                            constSeries = concatSeries(row,best_match,worst_match)
                            constDF = concatDF(constSeries,constDF)
                            search_tf = False
                            break
                        else:
                            pass
                    except:
                        pass
                #..Otherwise if the loop number is greater than the number of listed priorities,
                #  add row with "No Match" and formula NaN
                elif counted_loops > len(priorList):
                    constSeries = concatSeries(pd.Series({"Component RT":RTi,"Compound Name":"No Match",\
                                                          "Match Factor":float('nan'),"Formula":float('nan')}),\
                                                           best_match,worst_match)
                    constDF = concatDF(constSeries,constDF)
                    search_tf = False
                    break
                else:
                    pass
                #Separate into its own function momentarily
                #if 
                
            #Count one while loop
            counted_loops += 1

        
    return constDF

#Function to save dataframe to .csv file
def outputCSV(constDF_Dict, file_directory, infilenames):
    #Create names of exported files by adding "_UPP" to the name before .csv
    outfilenames = [x[:x.index('.csv')] + '_UPP' + x[x.index('.csv'):] for x in infilenames]
    #Create list of filepaths from export directory + filename.csv
    filepathList = [file_directory / outfilenames[i] for i in range(len(outfilenames))]
    #If export directory does not exist, create it
    filepathList[0].parent.mkdir(parents=True,exist_ok=True)
    
    #For every filename, save a .csv
    for i in range(len(infilenames)):
        constDF_Dict[infilenames[i]].to_csv(filepathList[i])
    
    return None
    
""" CODE """

#Unpack all .csv files in provided directory
print("[MAIN] Unpacking data from provided directory...")
UAData_raw = {}

for i in range(len(files)):
    UAData_raw[files[i]] = unpackUA(fileLoc[i])

print("[MAIN] Data unpacked.")

#Dictionaries for filtered and constrained data for each file
filterDF_Dict = {}
constDF_Dict = {}
#Dictionary for constrained data to be outputted
UAData_PP = {}
#For all files, run the constraint workflow
for i in range(len(files)):
    #Group retention times for all files
    print("[" + files[i] + "] Grouping retention times...")
    filterDF = groupRT(UAData_raw[files[i]])
    filterDF_Dict[files[i]] = filterDF
    #Apply constraints to all files
    print("[" + files[i] + "] Applying compound constraints...")
    constDF = constrain(filterDF, [noBar,softBar])
    constDF_Dict[files[i]] = constDF

#Save results
print("[MAIN] Saving results...")
outputCSV(constDF_Dict, expfileDir, files)
print("[MAIN] Files saved to " + str(expfileDir))

#Complete program
print("[MAIN] Unknowns post processing finished.")