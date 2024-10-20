#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT FOR LABELING A LIST OF COMPOUNDS ACCORDING TO PREDEFINED
COMPOUND TYPE RULES

Julia Hancock
7-9-2024

"""

""" PACKAGES """
import pandas as pd


""" CONTAIN DICTIONARIES """
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

#List of contains keys in order of priority
keyLoop = ['A','C','E','B','L']

#List of elements to be excluded and automatically labelled as 'O'
elementExclude = ['He','Li','Be','B','N','O','F','Ne','Na','Mg','Al','Si','P',\
                  'S','Cl','Ar','K','Ca','Sc','Ti','V','Cr','Mn','Fe','Co',\
                  'Ni','Cu','Zn']

""" FUNCTIONS """

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
    
    #Ordered list of keys to be looped through
    keyLoop = ['A','C','E','B','L']
    
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
            

""" CODE """

#Define file path
path = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/AutoQuant/data/example/raw data/example_GS2_FIDpMS.csv"

#Read csv at file path, assign to DataFrame importDF
importDF = pd.read_csv(path)

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
    







    
    