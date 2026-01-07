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
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

""" FUNCTIONS """

def updateDirectories(fileDir):

    #Import file information from json file
    with open(os.path.join(fileDir,'properties.json'),'r') as props_f:
        props = json.load(props_f)
    
    #Extract files directory
    D_files = props['file-directory']

    #Check the app directory, update as necessary
    D_appOut = checkApp(fileDir,props['app-directory'])

    #Check the documents directory, update as necessary using UI
    D_filesOut = checkDocuments(D_appOut,D_files)

    #Create propsOut
    propsOut = {'app-directory':D_appOut,'file-directory':D_filesOut}

    return propsOut


def checkApp(fileDir,D_app):
    """
    This function is used to check the validity of the app folder

    Parameters
    ----------
    fileDir : String
        Path to source directory
    D_app : String
        Path to saved apps directory
    Returns
    -------
    None
    """

    #If app directory is empty or not equal to fileDir, replace D_app
    if D_app != fileDir or D_app == "":

        #Define app directory as current file directory
        D_app = fileDir
        print("[Handle][Define] App directory updated, not saved")

    #Otherwise, pass
    else:
        print("[Handle][Define] App directory already valid")
        pass

    return D_app

def checkDocuments(D_app,D_files):
    """
    This function is used to check the validity of the documents folder to be used for data and resource storage

    Parameters
    ----------
    D_app : String
        Path to saved apps directory
    D_files : String
        Path to saved documents directory
    Returns
    -------
    None
    """
    
    def promptUser(msg,error_msg,D_app,D_files):
        """
        This function is used to prompt the user to update the documents folder

        Parameters
        ----------
        msg : String
            Prompt message
        error_msg : String
            Error message if user chooses not to update
        D_app : String
            Path to saved apps directory
        D_files : String
            Path to saved documents directory
        Returns
        -------
        None
        """
        
        def YNBox(msg):
            #Define response
            response = False

            #Pop up message box
            response = messagebox.askyesno("Warning",msg)

            return response
        
        #Initiate tkinter window
        promptroot = tk.Tk()
        promptroot.withdraw()

        response = YNBox(msg)

        if response:
            print("[Handle][Define] Updating documents folder...")
            #Close prompt UI
            promptroot.destroy()
            #Run documents UI
            D_files = setDocuments(D_app,D_files)
        else:
            print("[Handle][Define] Not updating documents folder")
            #Close UI
            promptroot.destroy()
            #Raise error
            raise ImportError(error_msg)
        
        
        
        return D_files

    def checkRecursive(D_app,D_files):

        #Define required subdirectories as list
        rqSubList = ["resources","response-factors","data",]

        #Define list of booleans to check when printing successful documents folder
        docTF = [False,False,False]

        #Check if directory exists
        if os.path.isdir(D_files) and D_files != "":
            docTF[0] = True

        else:
            print("[Handle][Define] Documents directory does not exist, please create it")
            D_files = setDocuments(D_app,D_files)
            #If directory is still nonexistent after selection, raise error
            if D_files == "":
                raise ImportError("Documents directory does not exist")
            else:
                pass

        #Get list of subdirectories
        subList = os.listdir(D_files)

        #Check if directory is empty
        if subList:
            docTF[1] = True

            #Check if directory contains every required subfolder
            if set(rqSubList).issubset(set(subList)):
                docTF[2] = True

            else:
                #Create new list of missing elements
                diff_list = [f"'{x}'" for x in rqSubList if x not in subList]
                #Create error message
                error_msg = "Documents directory is missing requiried subdirectories: " + ", ".join(diff_list)
                #Prompt user to change directory
                D_files = promptUser("The selected directory is missing required files, would you like to update it?",error_msg,D_app,D_files)

        else:
            #Prompt user to change directory
            D_files = promptUser("The selected directory is empty, would you like to update it?","Documents directory is empty",D_app,D_files)
            print(D_files)

        #If no errors or stops, print valid directory statement
        if all(docTF):
            print("[Handle][Define] Documents directory valid")

        #If at least one stop, rerun recursive function
        else:
            D_files = checkRecursive(D_app,D_files)

        return D_files
    
    #Run recursive function
    D_files = checkRecursive(D_app,D_files)

    return D_files


def setDocuments(D_app,D_files):
    """
    This function is used to check the validity of the documents folder to be used for data and resource storage

    Parameters
    ----------
    D_app : String
        Path to saved apps directory
    D_files : String
        Path to saved files directory
    Returns
    -------
    None
    """

    class docUI():

        def __init__(self,main,D_app,D_files):

            #Print initialize statement
            print("[Handle][Define][docUI] Documents selection program initiated")
            #Extract passed mainframe
            self.main = main
            #Extract passed file directory
            #self.D_files = fileDir
            #Extract passed properties file
            #self.props = propsIn.copy()
            #Define app directory
            self.D_app = D_app
            #Define file directory
            self.D_files = D_files

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

            return None
        
        def saveSelection(self):

            #Update directories
            self.D_files = self.docPath
            self.updateDocuments()

            #Close UI
            self.main.destroy()

            return None

        def updateDocuments(self):
            
            #Create properties dictionary
            self.props = {'app-directory':self.D_app,'file-directory':self.D_files}

            #Print app directory
            print("[Handle][Define] App directory set to {0}".format(self.D_app))

            #Print data files directory
            print("[Handle][Define] Data files directory set to {0}".format(self.D_files))

            #Save new directories to properties.json
            with open(os.path.join(self.D_app,'properties.json'),'w') as self.props_f:
                json.dump(self.props,self.props_f,indent=4)
            
            #Print save message
            print("[Handle][Define] Directories saved to properties.json")
            
            #Show save message
            messagebox.showinfo(title="Directories Saved",message="The app and documents directory have been updated")

            return None

        def getFileDirectory(self):

            return self.D_files
        
    root = tk.Tk()

    myDocUI = docUI(root,D_app,D_files)
    root.mainloop()

    print("[Handle][Define][docUI] Program terminated")
    D_files = myDocUI.getFileDirectory()

    return D_files
