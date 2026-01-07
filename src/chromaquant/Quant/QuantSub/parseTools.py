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

SUBPACKAGE FOR PARSING QUANTIFICATION INFORMATION

Julia Hancock
Started 12-29-2024

"""

""" PACKAGES """
import os
import datetime

""" FUNCTIONS """
#Function that evaluates runtime parameters
def evalRunParam(quantphases):

    #Write whether or not to run liquid and gas analysis based on system argument
    if quantphases == 'L':
        #Format is [Liquid Bool, Gas Bool]
        lgTF = [True,False]

    elif quantphases == 'G':
        lgTF = [False,True]

    elif quantphases == 'LG':
        lgTF = [True,True]

    else:
        lgTF = None
    
    return lgTF

#Function that finds most recent response factor file
def findRecentFile(prefix,suffix,path):

    #Files must be of the form prefix_mm-dd-yy.suffix

    #Function that checks whether the filtered files list is empty
    def checkEmpty(list):

        #If list is empty...
        if not list:
            
            return False
        
        #If list is not empty...
        else:

            return True

    #Get list of files in response factor directory
    files = os.listdir(path)

    #TEMPORARY FOR TESTING FILES
    #files = ['LRF_07-24-24.xlsx','LRF_07-29-24.xlsx','LRF_08-21-24.xlsx']

    #Predefine filtered files list
    filter_files = []

    #Get files with the right prefix by looping through dictionary
    for i in files:
        #If current file has the passed prefix...
        if prefix == i[:len(prefix)]:
            #Add current file to filtered files list
            filter_files.append(i)
        #Otherwise, pass
        else:
            pass
    
    #Check if filtered file list is empty
    checkTF = checkEmpty(filter_files)

    #Predefine filtered suffix list
    filter_suffix_files = []

    #If list if not empty...
    if checkTF:
        
        #Take filtered files list and find files with the correct suffix
        for i in filter_files:
            #If current file has the passed suffix...
            if suffix == i[len(i)-len(suffix):]:
                #Add current file to filtered files list
                filter_suffix_files.append(i)
            #Otherwise, pass
            else:
                pass

        #Check if filtered file list is empty
        checkTF = checkEmpty(filter_suffix_files)

        #If list is not empty...
        if checkTF:
            
            #If list has one element, return the full path to that element's path
            if len(filter_suffix_files) == 1:

                return os.path.join(path , filter_suffix_files[0])
            
            #Otherwise, filter the list based on which file is most recent
            else:

                #Define date format
                format = '%m-%d-%y'

                #Define current datetime
                current = datetime.datetime.now()

                #Predefine dictionary of datestrings, for each file get the date string and fill the respective dictionary value
                date_dict = {i : i[len(prefix)+1:len(i)-len(suffix)] for i in filter_suffix_files}

                #Convert string format into datetime format
                datetime_dict = {i : datetime.datetime.strptime(date_dict[i],format) for i in date_dict}

                #Get difference between current time and each file datetime
                for i in datetime_dict:
                    datetime_dict[i] = (current - datetime_dict[i]).total_seconds()

                #Select the most recent file
                recent_file = min(datetime_dict, key=datetime_dict.get)

                return os.path.join(path , recent_file)

        #If list is empty...
        else:
            #Break function and return None
            return None

    #If list is empty...
    else:
        #Break function and return None
        return None

#Define function that inserts a column to a CTCN Dataframe labeling the carbon number
def insertCN(CTCN_DF):
    
    #Get the length of the dataframe, take this to be the maximum carbon number
    CN_max = len(CTCN_DF)
    
    #Get a list of carbon numbers for each row
    CN_list = [i for i in range(1,CN_max+1)]
    
    #Insert this list as a new column at the beginning of the dataframe
    CTCN_DF.insert(loc=0, column='Carbon Number', value=CN_list)

    return CTCN_DF
