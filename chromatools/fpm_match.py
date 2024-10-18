"""
SCRIPT WHICH MATCHES FID AND MS PEAKS

Julia Hancock
Started 12/29/2023

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
import scipy

""" PARAMETERS """
#Default third order fit arguments for gas FID and MS peak matching
#a (x^3)
a_tof = 0.03
#b (x^2)
b_tof = -0.5839
#c (x)
c_tof = 5
#d
d_tof = -3.2099
#Combine into a list
fit_const = [a_tof,b_tof,c_tof,d_tof]


""" SAMPLE INFO """
#Write sample name
sname = 'example'

#Write sample phase ("L" or "G")
sphase = "G"

#Write whether or not to perform speculative labeling
splab_TF = False

#Specify the allowable error for both linear and speculative peak matching
peakError = 0.06

#Specify model, ("T" or "L")
model = "T"

#Specify the restrictions and preferences to be implemented in speculative labeling
#The first list contains properties which must match in order for something to be labelled
#The second dictionary contains properties which are preferred in deciding between multiple matches
#The dictionary should have key:value pairs of the form "kc_rsc":"allowable error between speculative entry and sample value"
#The preferences listed are applied in order such that the first preference is more valued than the last
restrictList = [['Gas'],{'Reaction Temperature (C)':5}]
#Start time for execution time
exec_start = datetime.now()

""" COMPOUND TYPE ASSIGNMENT VARIABLES """
#This dictionary contain lists of substrings to be checked against compound name strings to
#assign a compound type

#Six compound types exist: linear alkanes (L), branched alkanes (B), aromatics (A), cycloalkanes (C),
#alkenes/alkynes (E), and other (O)

#Each compound type abbreviation will have an entry in the dictionary corresponding to a list of
#substrings to be checked against a compound name string

contains = {'L':['methane','ethane','propane','butane','pentane','hexane','heptane','octane','nonane',\
                 'decane','undecane','hendecane','dodecane','tridecane','tetradecane','pentadecane','hexadecane','heptadecane','octadecane','nonadecane',\
                 'icosane','eicosane','heneicosane','henicosane','docosane','tricosane','tetracosane','pentacosane','hexacosane','cerane','heptacosane','octacosane','nonacosane',\
                 'triacontane','hentriacontane','untriacontane','dotriacontane','dicetyl','tritriacontane','tetratriacontane','pentatriacontane','hexatriacontane','heptatriacontane','octatriacontane','nonatriacontane',\
                 'tetracontane','hentetracontane','dotetracontane','tritetracontane','tetratetracontane','pentatetracontane','hexatetracontane','heptatetracontane','octatetracontane','nonatetracontane','pentacontane'],\
            
            'B':['iso','methyl','ethyl','propyl','butyl','pentyl','hexyl','heptyl','octyl','nonyl',\
                 'decyl','undecyl','dodecyl','tridecyl','tetradecyl','pentadecyl','hexadecyl','heptadecyl','octadecyl','nonadecyl',\
                 'icosyl','eicosyl','heneicosyl','henicosyl','docosyl','tricosyl','tetracosyl','pentacosyl','hexacosyl','heptacosyl','octacosyl','nonacosyl',\
                 'triacontyl','hentriacontyl','untriacontyl','dotriacontyl','tritriacontyl','tetratriacontyl','pentatriacontyl','hexatriacontyl','heptatriacontyl','octatriacontyl','nonatriacontyl',\
                 'tetracontyl','hentetracontyl','dotetracontyl','tritetracontyl','tetratetracontyl','pentatetracontyl','hexatetracontyl','heptatetracontyl','octatetracontyl','nonatetracontyl','pentacontyl'],
            
            'A':['benzyl','benzo','phenyl','benzene','toluene','xylene','mesitylene','durene','naphthalene','fluorene','anthracene','phenanthrene','phenalene',\
                 'tetracene','chrysene','triphenylene','pyrene','pentacene','perylene','corannulene','coronene','ovalene','indan','indene','tetralin'],\
            
            'C':['cyclo','menthane'],\
            
            'E':['ene','yne'],\
            
            'O':[]}

#Tuple of contains keys in order of priority
keyLoop = ('A','C','E','B','L')

#Tuple of elements to be excluded and automatically labelled as 'O'
elementExclude = ('He','Li','Be','B','N','O','F','Ne','Na','Mg','Al','Si','P',\
                  'S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co',\
                  'Ni','Cu','Zn')


""" DIRECTORIES """
#Main directory
cwd = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/AutoQuant/"

#Set up dictionary containing all relevant directories
direcDict = {'cwd':"/Users/connards/Desktop/University/Rorrer Lab/Scripts/AutoQuant/",  #Main directory
             'resources':cwd+'resources/',                  #Resources directory
             'DF_Dir':cwd+"data/"+sname+"/",                #Data file directory
             'DF_raw':cwd+"data/"+sname+"/raw data/",       #Raw data files directory
             'DFlog_Dir':cwd+"data/"+sname+"/log/"}         #Data file log directory

#Dictionary of substrings to add to sample name to create file names
sub_Dict = {'Gas TCD+FID':['_GS2_TCD_CSO.csv'],
            'Gas Labelled MS Peaks':['_GS1_UA_Comp_UPP.csv'],
            'Gas FID+MS':['_GS2_FIDpMS.csv'],
            'Liquid FID':['_LQ1_FID_CSO.csv'],
            'Liquid Labelled MS Peaks':['_LQ1_UA_Comp_UPP.csv'],
            'Liquid FID+MS':['_LQ1_FIDpMS.csv'],
            'Info':['_INFO.json']}


""" LOGGING """
#Get current datetime
now = datetime.now()
#Get current datetime string
nows = now.strftime('%Y%m%d')

#If log directory does not exist within sample folder, create it
if not os.path.exists(direcDict['DFlog_Dir']):
    os.makedirs(direcDict['DFlog_Dir'])

#Instantiate a logger
logger = logging.getLogger(__name__)
#Initialize logging file using current datetime
fh = logging.FileHandler(direcDict['DFlog_Dir']+'quantlog_'+nows+'.log')
logger.addHandler(fh)
#Set logging level
logger.setLevel(logging.INFO)
#Create a formatter and assign to logger
formatter = logging.Formatter('[%(filename)s] %(asctime)s - [%(levelname)s]: %(message)s')
fh.setFormatter(formatter)

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
        #Log that file wasn't found and a new one is being created
        logger.info('FIDpMS file not found for sample and phase, creating new...')
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
                #Create a log entry
                logger.info('FIDpMS file exists and contains manual and/or blank sourced entries')
                return fpmDF, True
            #Otherwise, if there exist no manually assigned peaks or labelled peaks with a blank source, return False
            else:
                #Create a log entry
                logger.info('FIDpMS file exists but does not contains manual or blank sourced entries')
                return fpmDF, False
            
        #If the FIDpMS file exists but has no peaks, return False
        else:
            #Create a log entry
            logger.info('FIDpMS file exists but contains no labelled peaks')
            return fpmDF, False

#Function describing a third order fit for gas analysis
def defaultGas(FIDRT,fpmDF,fit_const=[a_tof,b_tof,c_tof,d_tof]):
    """
    A function used to describe the default fit for gas analysis peak matching

    Parameters
    ----------
    FIDRT : Float
        A float describing the FID retention time requiring a corresponding MS retention time.
    fpmDF : DataFrame
        A dataframe containing FID and MS peak info.
    fit_const : List, optional
        A list of floats describing a third order fit. The default is [a_tof,b_tof,c_tof,d_tof].

    Returns
    -------
    MSRT : Float
        A float describing the calculated MS RT using the third order fit and the FID RT
    """
    
    MSRT = fit_const[0]*FIDRT**3+fit_const[1]*FIDRT**2+fit_const[2]*FIDRT+fit_const[3]
    
    return MSRT

#TODO: Function for creating a third order fit using manually matched peaks

#Function for creating a linear fit using manually matched peaks
def RTlinfit(fpmDF):
    
    #Get a new dataframe containing only rows with labelled peaks
    fpmDF_lab = fpmDF.loc[~fpmDF['Compound Name'].isna()]
    
    #Get a new dataframe containing only rows with manual/blank peaks
    fpmDF_mb = fpmDF_lab.loc[(fpmDF_lab['Compound Source']=='Manual') | (fpmDF_lab['Compound Source'].isna())]
    
    #If dataframe contains any rows with 'Manual' as a source..
    if 'Manual' in fpmDF_lab['Compound Source'].tolist():
        #If dataframe also contains rows with 'nan' as a source..
        if pd.isna(fpmDF_lab['Compound Source'].values).any():
            
            #Manual and blank counts are appropriately assigned
            manual_count = fpmDF_lab['Compound Source'].value_counts()['Manual']
            blank_count = fpmDF_lab['Compound Source'].isna().sum()
            #All count will include both manual and blank entries
            all_count = manual_count + blank_count
            
        #Otherwise, all count will only include manual entries
        else:
            manual_count = fpmDF_lab['Compound Source'].value_counts()['Manual']
            blank_count = 0
            all_count = manual_count
            
    #Else if dataframe contains anyrows with 'nan' as a source..
    elif pd.isna(fpmDF_lab['Compound Source'].values).any():
        #All count will include only blank entries
        manual_count = 0
        blank_count = fpmDF_lab['Compound Source'].isna().sum()
        all_count = fpmDF_lab['Compound Source'].isna().sum()
        
    #Otherwise, log that the provided dataframe has no manual or blank entries and return None or 0 for all returns
    else:
        logger.error('Linear fit function provided a dataframe without manual or blank entries')
        return None, [0,0,0]
    
    #If the blank count is larger than zero, log a warning stating that one or more entries contain a blank source
    if blank_count > 0:
        logger.warning("One or more labelled peaks in the FIDpMS file have no entry for Compound Source")
    #Otherwise, pass
    else:
        pass
    
    #Predefine variables for use in linear fitting
    peakDrift = 0      #Peak drift, the linear slope describing drift between FID and MS RT's
    peakOffset = 0     #Peak offset, the initial offset between FID and MS RT's
    peakDiff = 0       #Peak difference, the difference between a given FID and MS RT 
    r2 = 0             #Coefficient of determination, the r^2 value of a linear fit
    
    #If all_count is equal to 1..
    if all_count == 1:
        
        #Set the peak offset to the peak difference for the single labelled peak
        peakDiff = fpmDF_mb['FID RT'].iloc[0] - fpmDF_mb['MS RT'].iloc[0]
        peakOffset = peakDiff
        
    else:
        
        #Loop through every labelled peak, calculating the peak difference
        for i, row in fpmDF_mb.iterrows():
            peakDiff = row['FID RT'] - row['MS RT']
            #Add this peak difference to a new column in the dataframe
            fpmDF_mb.at[i,'peakDiff'] = peakDiff
        #Get a linear fit for peak drift and peak offset using peak differences as y-values and FID RT's as x-values
        peakDrift, peakOffset, r_value, p_value, std_err = scipy.stats.linregress(fpmDF_mb['FID RT'],fpmDF_mb['peakDiff'])
        #Get a coefficient of determination
        r2 = r_value**2
        #Get a list of all peak counts
        counts = [all_count,manual_count,blank_count]
        
    return fpmDF_mb, [peakDrift,peakOffset,r2], counts

#Function that estimates unknown MS RT's and matches FID and MS peaks using a provided linear fit 
def matchPeaksLinear(fpmDF,mDF,linfits,peakError=0.06):
    """
    Parameters
    ----------
    fpmDF : DataFrame
        Dataframe containing FID and MS peak info
    mDF : DataFrame
        Dataframe containing MS info about identified compounds (UA_UPP)
    linfits : List
        List containing info about a linear fit for estimated MS RT's in the form [m,b,r2]
    peakError : Float, optional
        Allowable error between estimated MS RT's and actual MS RT's. The default is 0.01.

    Returns
    -------
    fpmDF : DataFrame
        Dataframe containing FID and MS peak info
    """
    
    def matchOne(fpmDF,fpmiter,linfits,peakError):
        """
        Parameters
        ----------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        fpmiter : List
            List containing current index and row in fpmDF of interest in form [i,row]
        linfits : List
            List containing info about a linear fit for estimated MS RT's in the form [m,b,r2]
        peakError : float
            Allowable error between estimated MS RT's and actual MS RT's

        Returns
        -------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        """
        
        #Unpack fpmDF iterating info
        fpmi = int(fpmiter[0])
        fpmrow = fpmiter[1]
        
        #Estimate an MS RT for the row's FID RT using the linear fit
        est_MSRT = fpmrow['FID RT'] - (peakDrift*fpmrow['FID RT'] + peakOffset)
        #Compare the estimated MS RT to all real MS RT's, seeing if there is a match within error
        mDF_match = mDF.loc[(mDF['Component RT'] >= est_MSRT-peakError) & (mDF['Component RT'] <= est_MSRT+peakError)].copy()
        #If there is more than one match, select the entry with the smallest error
        if len(mDF_match) > 1:
            #Add an RT error to all mDF_match entries
            for i, row in mDF_match.iterrows():
                mDF_match.at[i,'RT Error'] = abs(fpmrow['FID RT']-est_MSRT)
            
            #Set mDF_match to the row with minimum RT Error
            mDF_match = mDF_match.nsmallest(1,'RT Error')
            
        #Reset the mDF_match index
        mDF_match = mDF_match.reset_index().copy()
        
        #If the length of mDF_match is greater than zero..
        if len(mDF_match) > 0:
            
            #Add the MS info to the FIDpMS dataframe
            fpmDF.at[fpmi,'MS RT'] = mDF_match.at[0,'Component RT']
            fpmDF.at[fpmi,'Compound Name'] = mDF_match.at[0,'Compound Name']
            fpmDF.at[fpmi,'Formula'] = mDF_match.at[0,'Formula']
            fpmDF.at[fpmi,'Match Factor'] = mDF_match.at[0,'Match Factor']
            fpmDF.at[fpmi,'Compound Source'] = 'Automatically assigned using a linear fit of manual peak assignments'
            
        #Otherwise, pass
        else:
            pass
        
        return fpmDF
    
    #Get peak drift and peak offset parameters from linfits, as well as coefficient of determination
    peakDrift = linfits[0]
    peakOffset = linfits[1]
    r2 = linfits[2]
    
    #Loop through every row in the dataframe
    for i, row in fpmDF.iterrows():
        #If the row's compound name is not blank
        if not pd.isna(row['Compound Name']):
            #If the row's compound source is either manual or blank, skip it
            if row['Compound Source'] == 'Manual' or pd.isna(row['Compound Source']):
                pass
            #Otherwise..
            else:
                #Match one FID peak
                fpmDF = matchOne(fpmDF, [i,row], linfits, peakError)
        #Otherwise, if the row's compound name is blank..
        else:
            #Match one FID peak
            fpmDF = matchOne(fpmDF, [i,row], linfits, peakError)
    
    return fpmDF

#Function that estimates unknown MS RT's and matches FID and MS peaks using a provided third order fit
def matchPeaksThird(fpmDF,mDF,fit_const,peakError=0.06):
    """
    Parameters
    ----------
    fpmDF : DataFrame
        Dataframe containing FID and MS peak info
    mDF : DataFrame
        Dataframe containing MS info about identified compounds (UA_UPP)
    fit_const : List
        A list of floats describing a third order fit.
    peakError : Float, optional
        Allowable error between estimated MS RT's and actual MS RT's. The default is 0.01.

    Returns
    -------
    fpmDF : DataFrame
        Dataframe containing FID and MS peak info
    """
    
    def matchOne(fpmDF,fpmiter,fit_const,peakError):
        """
        Parameters
        ----------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        fpmiter : List
            List containing current index and row in fpmDF of interest in form [i,row]
        fit_const : List
            A list of floats describing a third order fit.
        peakError : float
            Allowable error between estimated MS RT's and actual MS RT's

        Returns
        -------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        """
        
        #Unpack fpmDF iterating info
        fpmi = int(fpmiter[0])
        fpmrow = fpmiter[1]
        
        #Define x as fpmrow['FID RT] for convenience
        x = fpmrow['FID RT']
        #Estimate an MS RT for the row's FID RT using the third order fit
        est_MSRT = fit_const[0]*x**3 + fit_const[1]*x**2 + fit_const[2]*x + fit_const[3]
        #Compare the estimated MS RT to all real MS RT's, seeing if there is a match within error
        mDF_match = mDF.loc[(mDF['Component RT'] >= est_MSRT-peakError) & (mDF['Component RT'] <= est_MSRT+peakError)].copy()
        #If there is more than one match, select the entry with the smallest error
        if len(mDF_match) > 1:
            #Add an RT error to all mDF_match entries
            for i, row in mDF_match.iterrows():
                mDF_match.at[i,'RT Error'] = abs(mDF_match.at[i,'Component RT']-est_MSRT)
            
            #Set mDF_match to the row with minimum RT Error
            mDF_match = mDF_match.nsmallest(1,'RT Error')
            
        #Reset the mDF_match index
        mDF_match = mDF_match.reset_index().copy()
        
        #If the length of mDF_match is greater than zero..
        if len(mDF_match) > 0:
            
            #Add the MS info to the FIDpMS dataframe
            fpmDF.at[fpmi,'MS RT'] = mDF_match.at[0,'Component RT']
            fpmDF.at[fpmi,'Compound Name'] = mDF_match.at[0,'Compound Name']
            fpmDF.at[fpmi,'Formula'] = mDF_match.at[0,'Formula']
            fpmDF.at[fpmi,'Match Factor'] = mDF_match.at[0,'Match Factor']
            fpmDF.at[fpmi,'Compound Source'] = 'Automatically assigned using a predetermined third-order fit'
            
        #Otherwise, pass
        else:
            pass
        
        return fpmDF
    
    #Loop through every row in the dataframe
    for i, row in fpmDF.iterrows():
        #If the row's compound name is not blank
        if not pd.isna(row['Compound Name']):
            #If the row's compound source is either manual or a gasPeaks known peak match or blank, skip it
            if row['Compound Source'] == 'Manual' or row['Compound Source'] == 'Automatically assigned using gas pairs provided in resources' or pd.isna(row['Compound Source']):
                pass
            #Otherwise..
            else:
                #Match one FID peak
                fpmDF = matchOne(fpmDF, [i,row], fit_const, peakError)
        #Otherwise, if the row's compound name is blank..
        else:
            #Match one FID peak
            fpmDF = matchOne(fpmDF, [i,row], fit_const, peakError)
    
    return fpmDF
    
#Function that performs a subset of speculative labeling, using known peaks hard-coded in a file gasPairs_FIDpMS.csv 
def matchKnownPeaks(fpmDF,mDF,gp_rsc):
    def matchOne(fpmDF,fpmiter,gp_rsc):
        """
        Parameters
        ----------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        fpmiter : List
            List containing current index and row in fpmDF of interest in form [i,row]
        gp_rsc : DataFrame
            Dataframe containing opened gasPairs resource.
        peakError : float
            Allowable error between estimated MS RT's and actual MS RT's

        Returns
        -------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        """
        
        #Unpack fpmDF iterating info
        fpmi = int(fpmiter[0])
        fpmrow = fpmiter[1]
        
        #Search the gasPairs resource to see if any known peaks/RT's match the FID peak list
        for i, row in gp_rsc.iterrows():
            #Set gp_match to empty string
            gp_match = pd.Series()
            #Define error as two times the standard deviation for the FID RT in the gasPeaks resource
            gp_error = row['Stdev FID RT']*2
            #Extract the FID RT from the resource
            gp_FIDRT = row['Average FID RT']
            #If the current fpmrow FID RT is within the error bounds of an entry in the resource, match it
            #NOTE: prefers the first match, even if the next match is closer. Most resourceRT's are more than 
            #2*error away from each other
            if (fpmrow['FID RT'] >= gp_FIDRT - gp_error) and (fpmrow['FID RT'] <= gp_FIDRT + gp_error):
                gp_match = row
                break
            #Otherwise, pass
            else:
                pass
        
        #If gp_match is empty, pass
        if gp_match.empty:
            pass
        #Otherwise, add the match info
        else:
            #Add the resource match info to the FIDpMS dataframe
            fpmDF.at[fpmi,'Compound Name'] = gp_match['Species']
            fpmDF.at[fpmi,'Formula'] = gp_match['Formula']
            fpmDF.at[fpmi,'Compound Source'] = 'Automatically assigned using gas pairs provided in resources'
        
        return fpmDF
    
    #Loop through every row in the dataframe
    for i, row in fpmDF.iterrows():
        #If the row's compound name is not blank
        if not pd.isna(row['Compound Name']):
            #If the row's compound source is either manual or blank, skip it
            if row['Compound Source'] == 'Manual' or pd.isna(row['Compound Source']):
                pass
            #Otherwise..
            else:
                #Match one FID peak
                fpmDF = matchOne(fpmDF, [i,row], gp_rsc)
        #Otherwise, if the row's compound name is blank..
        else:
            #Match one FID peak
            fpmDF = matchOne(fpmDF, [i,row], gp_rsc)
    
    return fpmDF


#Function that performs speculative labeling to label FID peaks which do not have a match
def specLab(fpmDF,kc_rsc,sinfo,counts,peakError,restrictList):
    
    #Unpack restrictList
    trueRestrict, prefer = restrictList
    #Log that speculative labeling is being performed
    logger.info('Performing speculative labeling on {0} with {1} peaks, {2} of which are labelled: {3} sourced manually and {4} with an unknown source'.format(sinfo['Sample Name'],len(fpmDF),counts[0],counts[1],counts[2]))
    
    #Loop through every entry in fpmDF
    for i, row in fpmDF.iterrows():
        #Define a Boolean for use in determining whether to run the next if statement or not
        Bool_kc_check = True

        #If the compound name is blank or either form of "No Match"..
        if pd.isna(row['Compound Name']) or row['Compound Name'] == 'No Match' or row['Compound Name'] == 'No Match':
            
            #Get a copy of kc_rsc
            kc_check = kc_rsc.copy()
            #Find rows where the FID peak RT is within provided error
            kc_check = kc_check.loc[(kc_check['FID RT']>=row['FID RT']-peakError) & (kc_check['FID RT']<=row['FID RT']+peakError)]
            #Filter out rows that label the peak as No Match or No match
            kc_check = kc_check.loc[(kc_check['Compound Name']!='No Match') & (kc_check['Compound Name']!='No match')]
            
            #For every entry in trueRestrict, filter out rows where the entry property does not match
            for entry in trueRestrict:
                kc_check = kc_check.loc[kc_check[entry]==sinfo[entry]]
            
            #If kc_check has more than one row...
            if len(kc_check)>1:
                
                #Make a copy of kc_check
                kc_check_2 = kc_check.copy()
                
                #Loop through every entry in prefer
                for key in prefer:
                    
                    #Select rows in which the given entry property in prefer has a value within the provided range
                    kc_check_2 = kc_check.loc[(kc_check[key]>=sinfo[key]-prefer[key])&(kc_check[key]<=sinfo[key]+prefer[key])]
                    #If this results in a DataFrame with more than one entry, filter the original kc_check
                    if len(kc_check_2)>1:
                        kc_check = kc_check_2.copy()
                        pass
                    #If this results in a DataFrame with one entry, break the loop
                    elif len(kc_check_2)==1:
                        kc_check = kc_check_2.iloc[0].copy()
                        #Define a Boolean for use in determining whether to run the next if statement or not
                        Bool_kc_check = False
                        break
                    #If this results in a DataFrame with fewer than one entry (the only other possible option)..
                    else:
                        #Pass and do not apply this preference
                        pass
                
                #If kc_check still has more than one row..
                if len(kc_check)>1 and Bool_kc_check:
                    #Get the row with the highest match factor
                    kc_check = kc_check.loc[kc_check['Match Factor'].idxmax()]
                
                #Otherwise, pass
                else:
                    pass
                
            #Else if kc_check has only one row..
            elif len(kc_check)==1:
                #Convert the DataFrame into a Series
                kc_check = kc_check.iloc[0]
            #Otherwise, pass
            else:
                pass
            
            #If kc_check is not 0..
            if len(kc_check) > 0:
                #Add the new kc_check entry to fpmDF for the given row
                fpmDF.at[i,'Compound Name'] = kc_check['Compound Name']
                fpmDF.at[i,'Formula'] = kc_check['Formula']
                fpmDF.at[i,'Compound Source'] = 'Speculated based on {0}, which used {1} at {2}C and {3}psi'.format(kc_check['Sample Name'],kc_check['Catalyst'],kc_check['Reaction Temperature (C)'],kc_check['Reaction pressure (psi)'])
            #Otherwise, pass
            else:
                pass
            
        #Otherwise, pass
        else:
            pass
        
    return fpmDF


""" DATA IMPORTS """
#Import sample information from json file
with open(direcDict['DF_Dir']+sname+sub_Dict['Info'][0]) as sinfo_f:
    sinfo = json.load(sinfo_f)

#Change ISO date-time strings into datetime objects
sinfo['Start Time'] = datetime.fromisoformat(sinfo['Start Time'])
sinfo['End Time'] = datetime.fromisoformat(sinfo['End Time'])

#Calculate a reaction time using the start, end, and heat time values and add to sinfo
sinfo['Reaction Time (hr)'] = abs(sinfo['End Time']-sinfo['Start Time']).total_seconds()/3600 - sinfo['Heat Time']

#Run the file naming function
paths = fileNamer(sname,sphase,sub_Dict,direcDict['DF_raw'])

#Import MS UPP data
mDF = pd.read_csv(paths[1])

#Get only relevant rows of MS UPP data
mDF = mDF.loc[:,['Component RT','Compound Name','Formula','Match Factor']]

#Import known compounds resource
kc_rsc = pd.read_csv(direcDict['resources']+'known_compounds.csv')
#Filter known compounds to only include rows with the same catalyst
#AND compounds which were not identified by the current sample
kc_rsc = kc_rsc.loc[(kc_rsc['Catalyst']==sinfo['Catalyst Type'])&(kc_rsc['Sample Name']!=sinfo['Sample Name'])]

#Import gasPairs_FIDpMS.csv resource
gp_rsc = pd.read_csv(direcDict['resources']+'gasPairs_FIDpMS.csv')

""" CODE """
#Run the file checking function
fpmDF, tf = checkFile(paths[2],paths[0])

#If the specified model is linear...
if model == "L":
    #If the file contains manually matched peaks..
    if tf:
        #Run the linear fit function
        fpmDF_mb, linfits, counts = RTlinfit(fpmDF)
        #Run the peak matching function
        fpmDF = matchPeaksLinear(fpmDF,mDF,linfits,peakError)
        
    else:
        pass

#Otherwise, if the specified model is third order...
elif model == "T":
    #Run the gasPeaks_FIDpMS resource matching function
    fpmDF = matchKnownPeaks(fpmDF,mDF,gp_rsc)
    #Run the third order peak matching function
    fpmDF = matchPeaksThird(fpmDF,mDF,fit_const,peakError)  

#Otherwise, pass
else:
    pass
#Run the speculative labeling function
if splab_TF == "True":
    print("Running speculative labelling...")
    fpmDF = specLab(fpmDF, kc_rsc, sinfo, counts, peakError, restrictList)
else:
    pass
    
#Save the FIDpMS data
fpmDF.to_csv(paths[2])

#End time for execution time
exec_end = datetime.now()
#Execution time
exec_time = (exec_end-exec_start).total_seconds()*10**3
print("Time to execute: {:.03f}ms".format(exec_time))





