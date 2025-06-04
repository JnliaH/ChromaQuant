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
def setDocuments(props, propPath):
    """
    This function is used to select the documents folder to be used for data and resource storage

    Parameters
    ----------
    props : Object
        Imported properties.json object
    propPath : String
        Path to properties.json file

    Returns
    -------
    None
    """

    class docUI():

        def __init__(self,main):

            #Extract passed mainframe
            self.main = main

            #Configure mainframe
            self.main.title("Documents Directory Selection")
            self.main.geometry("300x120")
            self.main.resizable(False,False)

            #Define document path
            self.docPath = ""

            #Set up selection button
            self.openButton = tk.Button(root, text="Open Directory", command=self.selectDirectory)
            self.openButton.pack(padx=20,pady=(20,0))

            #Set up selected directory label
            self.directoryLabel = tk.Label(root, text="Selected Directory:")
            self.directoryLabel.pack(pady=(20,20))

            return None
        
        def selectDirectory(self):
            
            self.docPath = filedialog.askdirectory(title="Select preferred documents directory")
            
            if self.docPath:
                self.directoryLabel.config(text="Selected Directory: {0}".format(self.docPath))
                self.updateDirectory()

            else:
                pass

            return None

        def updateDirectory(self):

            return None

    root = tk.Tk()
    myDocUI = docUI(root)
        
    root.mainloop()

    print("[docUI] Program terminated")
    return None

setDocuments()