"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2024, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
	      URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SUBPACKAGE FOR MATCHING FID AND MS PEAKS ACCORDING TO A PASSED MODEL

Julia Hancock
Started 12/10/2024

"""

""" PACKAGES """
import pandas as pd

""" FUNCTIONS """

#Third order function for testing
fit = lambda FID_RT: 0.0252*FID_RT**3 - 0.5274*FID_RT**2 + 4.8067*FID_RT - 3.0243

#Function that estimates unknown MS RT's and matches FID and MS peaks using a provided fit
def matchPeaks(fpmDF,mDF,fit,peakError=0.06):

    """
    Parameters
    ----------
    fpmDF : DataFrame
        Dataframe containing FID and MS peak info
    mDF : DataFrame
        Dataframe containing MS info about identified compounds (UA_UPP)
    linfits : Function
        Function that returns an estimated MS RT with a passed FID RT
    peakError : Float, optional
        Allowable error between estimated MS RT's and actual MS RT's. The default is 0.01.

    Returns
    -------
    fpmDF : DataFrame
        Dataframe containing FID and MS peak info
    """
    
    def matchOne(fpmDF,fpmiter,fit,peakError):
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
        est_MSRT = fit(fpmrow['FID RT'])
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
                fpmDF = matchOne(fpmDF, [i,row], fit, peakError)
        #Otherwise, if the row's compound name is blank..
        else:
            #Match one FID peak
            fpmDF = matchOne(fpmDF, [i,row], fit, peakError)
    
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