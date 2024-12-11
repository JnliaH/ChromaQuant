"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2024, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
	      URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SUBPACKAGE FOR FILE NAMING AND HANDLING PROTOCOLS

Julia Hancock
Started 12/10/2024

"""

""" PACKAGES """
import os
import numpy as np
import pandas as pd

""" FUNCTIONS """

#Function for selecting FID peak, MS peak, and FIDpMS pathnames according to sample name and phase
def fileNamer(sname,sphase,sub_Dict,pathData):
    """
    Parameters
    ----------
    sname : STR
        The name of the sample.
    sphase : STR
        A string that describes whether sample is gas ("G") or liquid ("L").
    sub_Dict : Dict
        A dictionary of substrings to add to sample name to create file names
    pathData : STR
        A string containing the pathname to the datafiles directory
        
    Returns
    -------
    paths : List
        A list of pathnames to return.

    """

    #If sample phase is liquid, set pathnames accordingly
    if sphase == "L":

        pathFID = os.path.join(pathData,sname+sub_Dict['Liquid FID'][0])
        pathMS = os.path.join(pathData,sname+sub_Dict['Liquid Labelled MS Peaks'][0])
        pathFIDpMS = os.path.join(pathData,sname+sub_Dict['Liquid FID+MS'][0])
        
    #Else if sample phase is gas, set pathnames accordingly
    elif sphase == "G":

        pathFID = os.path.join(pathData,sname+sub_Dict['Gas TCD+FID'][0])
        pathMS = os.path.join(pathData,sname+sub_Dict['Gas Labelled MS Peaks'][0])
        pathFIDpMS = os.path.join(pathData,sname+sub_Dict['Gas FID+MS'][0])
        
    #Otherwise, set all paths to None
    else:

        pathFID = None
        pathMS = None
        pathFIDpMS = None
        
    paths = [pathFID,pathMS,pathFIDpMS]
    
    return paths
    
#Function for checking if FIDpMS file exists – creates it if necessary and imports/returns the data
def checkFile(fpmDir,fDir):
    """
    Parameters
    ----------
    fpmDir : STR
        A string containing the pathname of the FIDpMS file in question.
    fDir : STR
        A string containing the pathname of the FID file of the same sample/phase as the FIDpMS file.
        
    Returns
    -------
    fpmDF : DataFrame
        A DataFrame containing the contents of the FIDpMS file.
    exists : BOOL
        A boolean describing whether or not the relevant file exists and has manually added peaks.

    """

    #If FIDpMS file does not exist in data file directory, create it and return False
    if not os.path.exists(fpmDir):

        #print that file wasn't found and a new one is being created
        print('FIDpMS file not found for sample and phase, creating new...')

        #Read FID dataframe
        fDF = pd.read_csv(fDir)

        #Filter FID dataframe to only include FID rows, as gas samples may have TCD rows, and set to fpmDF
        fpmDF = fDF.loc[fDF['Signal Name'] == 'FID1A'].copy()

        #Rename FID RT and FID Area columns, as well as rename the Height column to MS RT
        fpmDF = fpmDF.rename(columns={'RT':'FID RT','Area':'FID Area','Height':'MS RT'})

        #Clear the contents of the MS RT column
        fpmDF['MS RT'] = np.nan

        #Create list of new columns to create
        lnc = ['Formula','Match Factor','Compound Source','Compound Type Abbreviation']
        
        #Loop through lnc, adding nan columns for each entry
        for i in lnc:
            fpmDF[i] = np.nan
        
        #Remove the Injection Data File Name and Signal Name columns
        fpmDF = fpmDF.drop(['Injection Data File Name','Signal Name'],axis=1).copy()

        #Save fpmDF to provided pathname
        fpmDF.to_csv(fpmDir, index=False)
        
        return fpmDF, False
    
    #Otherwise..
    else:

        fpmDF = pd.read_csv(fpmDir)

        #If the FIDpMS exists and there exist any peaks..
        if fpmDF['Compound Name'].any():

            #Define a new dataframe which includes all rows with labelled peaks
            fpmDF_labelled = fpmDF.loc[~fpmDF['Compound Name'].isna()]['Compound Source']

            #If those peaks are manually assigned or have a blank source, return the dataframe and True
            if 'Manual' in fpmDF_labelled.values.tolist() or pd.isna(fpmDF_labelled.values).any():

                #Print
                print('FIDpMS file exists and contains manual and/or blank sourced entries')

                return fpmDF, True
            
            #Otherwise, if there exist no manually assigned peaks or labelled peaks with a blank source, return False
            else:

                #Print
                print('FIDpMS file exists but does not contains manual or blank sourced entries')

                return fpmDF, False
            
        #If the FIDpMS file exists but has no peaks, return False
        else:

            #Print
            print('FIDpMS file exists but contains no labelled peaks')

            return fpmDF, False