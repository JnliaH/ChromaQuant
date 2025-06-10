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
from tkinter import messagebox
import importlib.util
import sys

""" FUNCTIONS """

def updateDirectories(fileDir):

    #Import file information from json file
    with open(os.path.join(fileDir,'properties.json'),'r') as props_f:
        props = json.load(props_f)

    
    #Check the app directory, update as necessary
    propsMid = checkApp(fileDir,props)

    #Check the documents directory, update as necessary using UI
    propsOut = checkDocuments(fileDir,propsMid)

    return propsOut


def checkApp(fileDir,propsIn):
    """
    This function is used to check the validity of the app folder

    Parameters
    ----------
    fileDir : String
    Path to source directory
    propsIn : Dictionary
        Dictionary containing key-value pairs unpacked from properties.json
    Returns
    -------
    None
    """

    #Extract app directory from passed dictionary
    D_app = propsIn['app-directory']
    #Initiate propsOut
    propsOut = propsIn.copy()

    #If app directory is empty or not equal to fileDir, replace D_app
    if D_app != fileDir or D_app == "":

        #Define app directory as current file directory
        D_app = fileDir
        #Set app-directory in props
        propsOut['app-directory'] = D_app
        print("[Handle][Define] App directory updated, not saved")

    #Otherwise, pass
    else:
        print("[Handle][Define] App directory already valid")
        pass

    return propsOut

def checkDocuments(fileDir,propsIn):
    """
    This function is used to check the validity of the documents folder to be used for data and resource storage

    Parameters
    ----------
    fileDir : String
        Path to source directory
    propsIn : Dictionary
        Dictionary containing key-value pairs unpacked from properties.json
    Returns
    -------
    None
    """
    
    #Define file directory
    D_files = propsIn['file-directory']

    #Initialize propsOut
    propsOut = propsIn.copy()

    #Define required subdirectories as list
    rqSubList = ["resources","response-factors","data","images"]

    #Define list of booleans to check when printing successful documents folder
    docTF = [False,False,False]

    #Check if directory exists
    if os.path.isdir(D_files) and D_files != "":

        docTF[0] = True
        pass

    else:
        print("[Handle][Define] Documents directory does not exist, please create it")
        D_files = setDocuments(fileDir,propsIn)
        #If directory is still empty after selection, raise error
        if D_files == "":
            raise ImportError("Documents directory does not exist")
        else:
            pass

        pass

    #Get list of subdirectories
    subList = os.listdir(D_files)

    #Check if directory is empty
    if subList:
        docTF[1] = True
        pass
    else:
        #Raise error
        raise ImportError("Documents directory is empty")

    #Check if directory contains every required subfolder
    if set(rqSubList).issubset(set(subList)):
        docTF[2] = True
        pass
    else:
        #Create new list of missing elements
        diff_list = [f"'{x}'" for x in rqSubList if x not in subList]
        #Create error message
        error_msg = "Documents directory is missing requiried subdirectories: " + ", ".join(diff_list)
        #Raise error
        raise ImportError(error_msg)

    #If no errors or stops, print valid directory statement
    if all(docTF):
        print("[Handle][Define] Documents directory already valid")
    #If needed to select folder, print save statement
    else:
        print("[Handle][Define] Documents directory updated")
        print("[Handle][Define] Directories saved to properties.json")

    #Redefine props
    propsOut['file-directory'] = D_files

    return propsOut


def setDocuments(fileDir, propsIn):
    """
    This function is used to check the validity of the documents folder to be used for data and resource storage

    Parameters
    ----------
    fileDir : String
        Path to source directory
    propsIn : Dictionary
        Dictionary containing key-value pairs unpacked from properties.json
    Returns
    -------
    None
    """

    class docUI():

        def __init__(self,main,fileDir,propsIn):

            #Print initialize statement
            print("[Handle][Define][docUI] Documents selection program initiated")
            #Extract passed mainframe
            self.main = main
            #Extract passed file directory
            self.fileDir = fileDir
            #Extract passed properties file
            self.props = propsIn.copy()
            #Define file directory
            self.D_files = self.props['file-directory']
            #Define app directory
            self.D_app = self.props['app-directory']

            #Configure mainframe
            self.main.title("Documents Selection")
            self.main.geometry("400x250")
            self.main.resizable(False,False)

            #Define document path
            self.docPath = ""

            #Set up selection button
            self.openButton = tk.Button(self.main, text="Open Directory", command=self.selectDocuments)
            self.openButton.pack(padx=20,pady=(20,10))

            #Set up selected directory label
            self.directoryLabel = tk.Label(self.main,text='Selected Directory:',font=('TKDefaultFont',12,'bold'))
            self.directoryLabel.pack(padx=20)
            
            #Set up selected directory textbox
            self.directoryText = tk.Text(self.main,wrap=tk.WORD,height=5)
            self.directoryText.pack(padx=20)

            #Set up apply button
            self.applyButton = tk.Button(self.main, text="Apply", command=self.applySelection)
            self.applyButton.pack(padx=20,pady=(10,0))

            #Set up save button
            self.saveButton = tk.Button(self.main, text="Save and Exit", command=self.saveSelection)
            self.saveButton.pack(padx=20,pady=(0,20))
            
            return None
        
        def selectDocuments(self):
            
            self.docPath = filedialog.askdirectory(title="Select preferred documents directory")
            
            if self.docPath:
                self.directoryText.delete('1.0',tk.END)
                self.directoryText.insert(tk.END,self.docPath)
                #self.directoryLabel.config(text="Selected Directory: {0}".format(self.docPath))
            
            else:
                pass

            return None
        
        def applySelection(self):

            #Update directories
            self.D_files = self.docPath
            self.updateDocuments()

            #Show save message
            messagebox.showinfo(title="Directories Saved",message="The app directory was saved as {0} and the file directory was saved as {1}".format(self.D_app,self.D_files))

            return None
        
        def saveSelection(self):

            #Update directories
            self.D_files = self.docPath
            self.updateDocuments()

            #Close UI
            self.main.destroy()

            return None

        def updateDocuments(self):
            
            #Set file directory in props
            self.props['file-directory'] = self.D_files

            #Save new directories to properties.json
            with open(os.path.join(self.fileDir,'properties.json'),'w') as self.props_f:
                json.dump(self.props,self.props_f,indent=4)

            #Print app directory
            print("[Handle][Define] App directory set to {0}".format(self.D_app))

            #Print data files directory
            print("[Handle][Define] Data files directory set to {0}".format(self.D_files))
            
            return None

        def getFileDirectory(self):

            return self.D_files
        
    root = tk.Tk()

    myDocUI = docUI(root,fileDir,propsIn)
    root.mainloop()

    print("[Handle][Define][docUI] Program terminated")
    D_files = myDocUI.getFileDirectory()

    return D_files

#updateDirectories("/Users/connards/Desktop/chromaquant/src/chromaquant")