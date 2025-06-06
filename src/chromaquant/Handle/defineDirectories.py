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

SCRIPT FOR USER-DEFINED DATA DIRECTORY

Julia Hancock
6-3-2025

*Inspired by example at https://www.w3resource.com/python-exercises/tkinter/python-tkinter-dialogs-and-file-handling-exercise-3.php
"""

""" PACKAGES """
import json
import os
import getpass
import tkinter as tk
from tkinter import filedialog
import importlib.util
import sys

""" FUNCTIONS """

def checkDocuments(fileDir):
    """
    This function is used to check the validity of the documents folder to be used for data and resource storage

    Parameters
    ----------
    fileDir : String
        Path to source directory

    Returns
    -------
    None
    """

    #Import file information from json file
    with open(os.path.join(fileDir,'properties.json'),'r') as props_f:
        props = json.load(props_f)
    
    #Define file directory
    D_files = props['file-directory']

    #Define required subdirectories as list
    rqSubList = ["resources","response-factors","data"]

    #Check if directory exists
    if os.path.isdir(fileDir) and fileDir != "":
        pass
    else:
        print("Documents directory does not exist, please create it")
        setDocuments(fileDir,props)
        pass

    #Get list of subdirectories
    subList = os.listdir(fileDir)

    #Check if directory is empty
    if not subList:
        pass
    else:
        raise ImportError("Documents directory is empty")

    #Check if directory contains every required subfolder
    if set(rqSubList).issubset(set(subList)):
        pass
    else:
        raise ImportError("Documents directory is missing requiried subdirectories")

    return None


def setDocuments(fileDir, props):
    """
    This function is used to select the documents folder to be used for data and resource storage

    Parameters
    ----------
    fileDir : String
        Path to source directory
    props : Object
        Imported properties.json object

    Returns
    -------
    None
    """

    class docUI():

        

        def __init__(self,main,props):

            #Extract passed mainframe
            self.main = main

            #Configure mainframe
            self.main.title("Documents Directory Selection")
            self.main.geometry("300x120")
            self.main.resizable(False,False)

            #Define document path
            self.docPath = ""

            #Set up selection button
            self.openButton = tk.Button(root, text="Open Directory", command=lambda: self.selectDirectory(props))
            self.openButton.pack(padx=20,pady=(20,0))

            #Set up selected directory label
            self.directoryLabel = tk.Label(root, text="Selected Directory:")
            self.directoryLabel.pack(pady=(20,20))

            
            return None
        
        def selectDirectory(self,props):
            
            self.docPath = filedialog.askdirectory(title="Select preferred documents directory")
            
            if self.docPath:
                self.directoryLabel.config(text="Selected Directory: {0}".format(self.docPath))
                self.updateDirectory(props)

            else:
                pass

            return None

        def updateDirectory(self,props):

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

            return None

    root = tk.Tk()
    myDocUI = docUI(root,props)
        
    root.mainloop()

    print("[docUI] Program terminated")
    return None

setDocuments()