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

SCRIPT FOR HANDLING FILE DIRECTORIES

Julia Hancock
7-29-2024
"""

""" PACKAGES """
import json
import os
import getpass

""" FUNCTIONS """

def handle(fileDir):
    #fileDir is the passed absolute directory of the currently running file
    
    #Import sample information from json file
    with open(os.path.join(fileDir,'properties.json'),'r') as props_f:
        props = json.load(props_f)
    
    #Define file directory
    D_files = props['file-directory']
    #Define app directory
    D_app = props['app-directory']
    #Get current user
    login = getpass.getuser()
    
    #If file directory has default user somewhere, insert current user
    if "[user]" in D_files:
        
        D_files = D_files.replace("[user]",login)
    
    #Otherwise, pass
    else:
        print("else")
        pass
    
    #If app directory is empty or not equal to fileDir or [user] version, replace D_app
    if D_app != fileDir or D_app != fileDir.replace(login,"[user]") or D_app == "":
        D_app = fileDir
        #Prepare 
        props['app-directory'] = fileDir.replace(login,"[user]")
        
        with open(os.path.join(fileDir,'properties.json'),'w') as props_f:
            json.dump(props,props_f,indent=4)
    
    #Otherwise, pass
    else:
        pass
    
    #Redefine app directory
    D_app = fileDir
    
    #Print data files directory
    print("[Handle] Data files directory set to {0}".format(D_files))
    
    #Define resources directory
    D_rsc = os.path.join(D_files,'resources')
    
    #Define theme directory
    D_theme = os.path.join(D_rsc,'forest','forest-light.tcl')
    
    #Define response factors directory
    D_rf = os.path.join(D_files,'response-factors')
    
    #Define data directory
    D_data = os.path.join(D_files,'data')
    
    #Define images directory
    D_img = os.path.join(D_files,'images')
    
    #Return directories as a dictionary
    return {'files':D_files,'resources':D_rsc,'theme':D_theme,'rf':D_rf,'data':D_data,'images':D_img}