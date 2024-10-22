"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2024, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
	      URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

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

""" FID AND MS MATCHING MAIN FUNCTION"""
def main_AutoFpmMatch(sname,sphase,splab_TF,model,directories):

    """ PARAMETERS """
    print("[AutoFpmMatch] Defining parameters...")
    #Default third order fit arguments for gas FID and MS peak matching
    #a (x^3)
    a_tof = 0.0252
    #b (x^2)
    b_tof = -0.5274
    #c (x)
    c_tof = 4.8067
    #d
    d_tof = -3.0243
    #Combine into a list
    fit_const = [a_tof,b_tof,c_tof,d_tof]

    """ PROCESSING SYSTEM ARGUMENTS """
    print("[AutoFpmMatch] Processing system arguments...")
    #Specify the allowable error for linear, third order, and speculative peak matching
    peakError = 0.06

    #Specify the allowable error for direct FID-MS RT matching
    peakErrorRT = 0.05

    #Specify the restrictions and preferences to be implemented in speculative labeling
    #The first list contains properties which must match in order for something to be labelled
    #The second dictionary contains properties which are preferred in deciding between multiple matches
    #The dictionary should have key:value pairs of the form "kc_rsc":"allowable error between speculative entry and sample value"
    #The preferences listed are applied in order such that the first preference is more valued than the last
    restrictList = [['Gas'],{'Reaction Temperature (C)':5}]

    """ COMPOUND TYPE ASSIGNMENT VARIABLES """
    print("[AutoFpmMatch] Defining compound type variables...")
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
                
                'B':['iso','neo','methyl','ethyl','propyl','butyl','pentyl','hexyl','heptyl','octyl','nonyl',\
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
    print("[AutoFpmMatch] Finding directories...")

    #Unpack directories from passed variable
    #Primary files directory
    files = directories['files']
    #Resources directory
    RE_Dir = directories['resources']
    #Theme directory
    theme_Dir = directories['theme']
    #Response factor directory
    RF_Dir = directories['rf']
    #Data directory
    DF_Dir = directories['data']
    #Images directory
    img_Dir = directories['images']
    #Data file log directory
    DFlog_Dir = os.path.join(DF_Dir,sname,'log')
    #Data file breakdowns directory
    DFbreak_Dir = os.path.join(DF_Dir,sname,'breakdowns')
    #Raw data file directory
    Raw_Dir = os.path.join(DF_Dir,sname,'raw data')

    #Dictionary of substrings to add to sample name to create file names
    sub_Dict = {'Gas TCD+FID':['_GS2_TCD_CSO.csv'],
                'Gas Labelled MS Peaks':['_GS1_UA_Comp_UPP.csv'],
                'Gas FID+MS':['_GS2_FIDpMS.csv'],
                'Liquid FID':['_LQ1_FID_CSO.csv'],
                'Liquid Labelled MS Peaks':['_LQ1_UA_Comp_UPP.csv'],
                'Liquid FID+MS':['_LQ1_FIDpMS.csv'],
                'Info':['_INFO.json']}


    """ LOGGING """
    print("[AutoFpmMatch] Initializing logging [WIP]...")
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
    fh = logging.FileHandler(os.path.join(DFlog_Dir,'quantlog_'+nows+'.log'))
    logger.addHandler(fh)
    #Set logging level
    logger.setLevel(logging.INFO)
    #Create a formatter and assign to logger
    formatter = logging.Formatter('[%(filename)s] %(asctime)s - [%(levelname)s]: %(message)s')
    fh.setFormatter(formatter)

    """ FUNCTIONS """
    print("[AutoFpmMatch] Defining functions...")
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

    #Function that matches FID and MS peaks by their retention time
    def matchRT(fpmDF,mDF,peakError=0.06):
        """
        Parameters
        ----------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        mDF : DataFrame
            Dataframe containing MS info about identified compounds (UA_UPP)
        peakError : Float, optional
            Allowable error between estimated MS RT's and actual MS RT's. The default is 0.01.

        Returns
        -------
        fpmDF : DataFrame
            Dataframe containing FID and MS peak info
        """
        
        def matchOne(fpmDF,fpmiter,peakError):
            """
            Parameters
            ----------
            fpmDF : DataFrame
                Dataframe containing FID and MS peak info
            fpmiter : List
                List containing current index and row in fpmDF of interest in form [i,row]
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
            
            #Compare the FID RT to the MS RT, collecting all matches within the specified peak error
            mDF_match = mDF.loc[(mDF['Component RT'] >= fpmrow['FID RT']-peakError) & (mDF['Component RT'] <= fpmrow['FID RT']+peakError)].copy()
            #If there is more than one MS RT match, select the entry with the smallest error from the FID RT
            if len(mDF_match) > 1:
                #Add an RT error to all mDF_match entries
                for i, row in mDF_match.iterrows():
                    mDF_match.at[i,'RT Error'] = abs(fpmrow['FID RT']-row['Component RT'])
                
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
                fpmDF.at[fpmi,'Compound Source'] = 'Automatically assigned by comparing FID and MS retention times'
                
            #Otherwise, pass
            else:
                pass
            
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
                    fpmDF = matchOne(fpmDF, [i,row], peakError)
            #Otherwise, if the row's compound name is blank..
            else:
                #Match one FID peak
                fpmDF = matchOne(fpmDF, [i,row], peakError)
        
        return fpmDF

    #Function that performs compound type abbreviation assignment
    def ctaAssign(importDF, contains, keyLoop, elementExclude):

        #Function that returns a compound type abbreviation corresponding to a compound
        def assignType(compoundName,contains,keyLoop):
            
            #Define default compound type abbreviation as 'O'
            CTA = 'O'
            
            #Function that accepts a list of substrings to check against a string and returns a boolean
            def stringSearch(string,subList):
                #Define export boolean default value
                checkTF = False
                #For every substring in subList...
                for i in range(len(subList)):
                    
                    #If the substring can be found in the string...
                    if subList[i] in string:
                        #Assign boolean to True and break
                        checkTF = True
                        break
                    #Otherwise, pass
                    else:
                        pass
                
                return checkTF
            
            #Loop through every key (compound type abbreviation) in contains
            for i in keyLoop:
                
                #If at least one substring in the key's list is found in compoundName...
                if stringSearch(compoundName,contains[i]):
                    #Assign the compound type abbreviation to the current key and break the loop
                    CTA = i
                    break
                #Otherwise, pass
                else:
                    pass
            
            return CTA

        #Function that checks if formula string contains any of a list of elements
        def checkElements(compoundFormula,elementList):
            #Assign default export boolean to False
            checkTF = False
            
            #For every substring in elementList...
            for i in range(len(elementList)):
                #If the substring can be found in the compound formula...
                if elementList[i] in compoundFormula:
                    #Set boolean to True and break
                    checkTF = True
                    break
                #Otherwise, pass
                else:
                    pass
            
            return checkTF

        #For every entry in the csv, assign a compound type abbreviation
        for i, row in importDF.iterrows():
            
            #Retrieve compound name and formula from row entry
            compoundName = row['Compound Name']
            compoundFormula = row['Formula']
            
            #If the compound formula is a string...
            if isinstance(compoundFormula,str):
                
                #If the formula contains excluded elements...
                if checkElements(compoundFormula,elementExclude):
                    
                    #Assign 'O' to the row's compound type abbreviation entry
                    importDF.at[i,'Compound Type Abbreviation'] = 'O'
                
                #Otherwise...
                else:
                    
                    #If the compound name is a string...
                    if isinstance(compoundName,str):
                    
                        #Change compound name to lowercase
                        compoundName = compoundName.lower()
                        #Get a corresponding compound type abbreviation
                        CTA = assignType(compoundName, contains, keyLoop)
                        #Assign this CTA to the row's compound type abbreviation entry
                        importDF.at[i,'Compound Type Abbreviation'] = CTA
                    
                    #Otherwise, pass
                    else:
                        pass
        
        return importDF

    #Define function that loops through every row in a DataFrame and modifies rows with duplicate compounds
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

    """ DATA IMPORTS """
    print("[AutoFpmMatch] Importing data...")
    #Import sample information from json file
    with open(os.path.join(DF_Dir,sname,sname+sub_Dict['Info'][0])) as sinfo_f:
        sinfo = json.load(sinfo_f)

    #Change ISO date-time strings into datetime objects
    sinfo['Start Time'] = datetime.fromisoformat(sinfo['Start Time'])
    sinfo['End Time'] = datetime.fromisoformat(sinfo['End Time'])

    #Calculate a reaction time using the start, end, and heat time values and add to sinfo
    sinfo['Reaction Time (hr)'] = abs(sinfo['End Time']-sinfo['Start Time']).total_seconds()/3600 - sinfo['Heat Time']

    #Run the file naming function
    paths = fileNamer(sname,sphase,sub_Dict,Raw_Dir)

    #Import MS UPP data
    mDF = pd.read_csv(paths[1])

    #Get only relevant columns of MS UPP data
    mDF = mDF.loc[:,['Component RT','Compound Name','Formula','Match Factor']]

    #Import known compounds resource
    kc_rsc = pd.read_csv(os.path.join(RE_Dir,'known_compounds.csv'))
    #Filter known compounds to only include rows with the same catalyst
    #AND compounds which were not identified by the current sample
    kc_rsc = kc_rsc.loc[(kc_rsc['Catalyst']==sinfo['Catalyst Type'])&(kc_rsc['Sample Name']!=sinfo['Sample Name'])]

    #Import gasPairs_FIDpMS.csv resource
    gp_rsc = pd.read_csv(os.path.join(RE_Dir,'gasPairs_FIDpMS.csv'))

    """ CODE """
    print("[AutoFpmMatch] Checking files...")
    #Run the file checking function
    fpmDF, tf = checkFile(paths[2],paths[0])

    #If the specified model is linear...
    if model == "L":
        #If the file contains manually matched peaks..
        if tf:
            print("[AutoFpmMatch] Matching by linear fit...")
            #Run the linear fit function
            fpmDF_mb, linfits, counts = RTlinfit(fpmDF)
            #Run the peak matching function
            fpmDF = matchPeaksLinear(fpmDF,mDF,linfits,peakError)
            
        else:
            pass

    #Otherwise, if the specified model is third order...
    elif model == "T":
        print("[AutoFpmMatch] Matching by third order fit...")
        #Run the gasPeaks_FIDpMS resource matching function
        fpmDF = matchKnownPeaks(fpmDF,mDF,gp_rsc)
        #Run the third order peak matching function
        fpmDF = matchPeaksThird(fpmDF,mDF,fit_const,peakError)  

    #Otherwise, if the specified model is retention time match...
    elif model == "R":
        print("[AutoFpmMatch] Matching by retention time...")
        #Run the liquid retention time matching function
        fpmDF = matchRT(fpmDF,mDF,peakErrorRT)

    #Otherwise, pass
    else:
        pass

    #Run the speculative labeling function
    if splab_TF == "True":
        print("[AutoFpmMatch] Running speculative labeling...")
        fpmDF = specLab(fpmDF, kc_rsc, sinfo, counts, peakError, restrictList)
    else:
        pass
    
    print("[AutoFpmMatch] Matching complete.")
    
    print("[AutoFpmMatch] Assigning compound type abbreviations...")
    #Run the compound type abbreviation assignment function
    fpmDF = ctaAssign(fpmDF, contains, keyLoop, elementExclude)
    print("[AutoFpmMatch] Handling duplicates...")
    #Run the duplicate handling function
    fpmDF = duplicateHandle(fpmDF)

    print("[AutoFpmMatch] Saving results...")
    #Save the FIDpMS data
    fpmDF.to_csv(paths[2],index=False)
    
    print("[AutoFpmMatch] Matching complete.")
    #Close main function by returning
    return None



