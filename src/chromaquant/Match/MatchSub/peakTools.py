"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2024, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
	      URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

SUBPACKAGE FOR POSTPROCESSING AFTER MATCHING

Julia Hancock
Started 12/10/2024

"""

""" PACKAGES """
import pandas as pd

""" FUNCTIONS """

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
            DF_return = pd.DataFrame()
            
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
    
    #Initialize a DataFrame for the logic output
    DF_logic = pd.DataFrame()
    
    #Initialize a DataFrame for the output DF, create a copy of original DF in case there are no duplicates
    DF_done = DF.copy()

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