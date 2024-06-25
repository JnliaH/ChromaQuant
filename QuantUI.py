#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

SCRIPT FOR SIMPLIFYING ANALYSIS WORKFLOW

Julia Hancock
Started 01-04-2024

"""

""" PACKAGES """

import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter.font as tkFont
import os
import subprocess
import sys

""" PARAMETERS """

version = "1.0"

""" DIRECTORIES """
#Main directory
cwd = os.getcwd()+"/"
#Data directory
DF_Dir = cwd+"data/"
#Response factors directory
RF_Dir = cwd+"response-factors/"
#Resources directory
RE_Dir = cwd+"resources/"

""" DATA SEARCH """

#Get a list of all available sample data directories (excluding "old") in the data files directory
sampleList = [f.name for f in os.scandir(DF_Dir) if f.is_dir() if f.name != "old"]


""" FUNCTIONS """
#Function for setting up UI window with styles and configurations
def uiSetup(theme_Dir):
    #Initialize UI window
    root = ThemedTk(theme='adapta')

    # Import the tcl file with the tk.call method
    root.tk.call('source', theme_Dir)  # Put here the path of your theme file

    # Set the theme with the theme_use method
    style = ttk.Style(root)
    style.theme_use('forest-light')  # Theme files create a ttk theme, here you can put its name
    #Set up style button font
    style.configure('QuantButton.TButton',font=('TKDefaultFont',16))
    #Set up style accent button font
    style.configure('Accent.TButton',font=('TKDefaultFont',16))
    #Set up labelframe font
    style.configure('QuantLabelframe.TLabelframe.Label',font=('TKDefaultFont',16))

    root.geometry("960x480")
    root.title("Data Analysis Workflow")
    root.resizable(0,0)

    #Create font objects
    title_font = tkFont.Font(size=18)   #Title font

    #style.theme_use('forest')
    #Configure the grid
    root.columnconfigure(0,weight=2)
    root.columnconfigure(1,weight=2)
    root.columnconfigure(2,weight=2)
    root.columnconfigure(3,weight=2)

    #Create a main frame
    mainframe = ttk.Frame(root)
    mainframe.grid(column=0,row=0)

    #Add title text
    tk.Label(mainframe,text="Rorrer Lab data analysis workflow v"+version,font=title_font).grid(column=0,row=0,columnspan=4,pady=5)
    return root, mainframe

#Function for sample selection combobox
def on_select(event):
    
   global sname
   sname = sampleBox.get()
   print("User selected "+sampleBox.get())
   return sampleBox.get()

#Function for fidpms phase selection combobox
def fidpms_select(event):
    
    global sphase
    sphase = fpmBox.get()
    
    #Convert to appropriate format
    if sphase == "Gas":
        sphase = "G"
    elif sphase == "Liquid":
        sphase = "L"
    

#Function for fidpms speculative labeling combobox
def fidpms_select2(event):
    
    global specLabTF
    specLabTF = fpm2Box.get()
    
    #Convert to appropriate format
    if specLabTF == "Yes":
        specLabTF = "True"
    elif specLabTF == "No":
        specLabTF = "False"

#Function for quant phase selection combobox
def quant_select(event):
    
    global quantphases
    quantphases = logBox.get()


#Function for running FIDpMS script
def runFIDpMS(event):
    print("User selected sample name {0} with phase {2} and entered {1} for running speculative labeling".format(sname,specLabTF,sphase))
    #If any of the required fields are empty, pass
    if sname == "" or specLabTF == "" or sphase == "":
        pass
    #Otherwise, run the FIDpMS script
    else:
        print("Running FIDpMS script...")
        
        try:
            subprocess.run(['python','AutoFPMMatch.py',sname,sphase,specLabTF], text=True, check=True)
            print("Program complete")
        except subprocess.CalledProcessError as e:
            print(f'Command {e.cmd} failed with error {e.returncode}')
    
    return None

#Function for running quant script
def runQuant(event):
    print("User selected sample name {0} with phase(s) {1}".format(sname,quantphases))
    #If any of the required fields are empty, pass
    if sname == "" or quantphases == "":
        print("User did not enter a value for at least one required argument, canceling script run")
        pass
    #Otherwise, run the FIDpMS script
    else:
        print("Running Quantification script...")
        
        try:
            subprocess.run(['python','AutoQuantification.py',sname,quantphases], text=True, check=True)
            print("Program complete")
        except subprocess.CalledProcessError as e:
            print(f'Command {e.cmd} failed with error {e.returncode}')
    
    return None


""" CODE """

#Run the UI setup
root, mainframe = uiSetup(RE_Dir+"forest/forest-light.tcl")

#SAMPLE SELECTION
#Add a frame for selecting the sample
sampleFrame = ttk.Frame(mainframe)
sampleFrame.grid(column=0,row=1,pady=5,padx=10)

#Add text to the top of the sample frame
tk.Label(sampleFrame,text='Select a sample to analyze:').grid(column=0,row=0)
sampleVar = tk.StringVar()
sampleBox = ttk.Combobox(sampleFrame,textvariable=sampleVar)
sampleBox['values'] = sampleList
sampleBox.state(["readonly"])
sampleBox.grid(column=0,row=1)

#Bind the sampleBox to a function
sampleBox.bind("<<ComboboxSelected>>",on_select)

"""
#SAMPLE INFO WIDGET
#Add a frame for adding/editing sample info
sinfo_content = ttk.LabelFrame(mainframe,text='Sample Info Editor',style='QuantLabelframe.TLabelframe')
sinfo_content.grid(column=0,row=2,pady=10,padx=10)
sinfo_content.columnconfigure(0,weight=1)

#Add a start button for adding/editing sample info
sinfo_sbutton = ttk.Button(sinfo_content,text="\n\n\nStart Editor\n\n\n",width=20,style='QuantButton.TButton')
sinfo_sbutton.grid(column=0,row=2,pady=40,padx=20) 
"""

"""
#UAUPP WIDGET
#Add a frame
uaUPP_content = ttk.LabelFrame(mainframe,text='Unknowns Analysis Postprocessing',style='QuantLabelframe.TLabelframe')
uaUPP_content.grid(column=0,row=2,pady=10,padx=10)
uaUPP_content.columnconfigure(0,weight=1)

#Add a start button
uaUPP_sbutton = ttk.Button(uaUPP_content,text="\n\n\nStart Widget\n\n\n",width=20,style='QuantButton.TButton')
uaUPP_sbutton.grid(column=0,row=2,pady=40,padx=20)
"""



#FIDPMS WIDGET
#Add a frame
fidpms_content = ttk.LabelFrame(mainframe,text='Peak Matching',style='QuantLabelframe.TLabelframe')
fidpms_content.grid(column=0,row=2,pady=10,padx=10)
fidpms_content.columnconfigure(0,weight=1)

#Add text to the top of the frame
tk.Label(fidpms_content,text='Please enter all information').grid(column=0,row=0,columnspan=2,padx=20)

#Set up a combobox for selecting liquid or gas
tk.Label(fidpms_content,text='Is the sample liquid or gas?').grid(column=0,row=1,padx=10,pady=20)
fpmVar = tk.StringVar()
fpmBox = ttk.Combobox(fidpms_content,textvariable=fpmVar)
fpmBox['values'] = ['Liquid','Gas']
fpmBox.state(["readonly"])
fpmBox.grid(column=1,row=1,padx=10)

#Bind the combobox to a function
fpmBox.bind("<<ComboboxSelected>>",fidpms_select)

#Set up a combobox for selecting liquid or gas
tk.Label(fidpms_content,text='Perform speculative labeling?').grid(column=0,row=2,padx=10,pady=20)
fpm2Var = tk.StringVar()
fpm2Box = ttk.Combobox(fidpms_content,textvariable=fpm2Var)
fpm2Box['values'] = ['Yes','No']
fpm2Box.state(["readonly"])
fpm2Box.grid(column=1,row=2,padx=10)

#Bind the combobox to a function
fpm2Box.bind("<<ComboboxSelected>>",fidpms_select2)

#Add a start button
fidpms_sbutton = ttk.Button(fidpms_content,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton')
fidpms_sbutton.grid(column=0,row=3,pady=20,padx=20,columnspan=2)
#Bind the button to a function to run the appropriate script
fidpms_sbutton.bind("<Button-1>",runFIDpMS)


#QUANT WIDGET
#Add a frame
quant_content = ttk.LabelFrame(mainframe,text='Quantification',style='QuantLabelframe.TLabelframe')
quant_content.grid(column=1,row=2,pady=20,padx=10)
quant_content.columnconfigure(0,weight=1)

#Add text to the top of the frame
tk.Label(quant_content,text='Please enter all information').grid(column=0,row=0,columnspan=2,padx=20)
#Set up a combobox for selecting liquid or gas
tk.Label(quant_content,text='Does the sample have liquid and/or gas components?').grid(column=0,row=1,padx=10,pady=20)
logVar = tk.StringVar()
logBox = ttk.Combobox(quant_content,textvariable=logVar)
logBox['values'] = ['Liquid','Gas','Liquid and Gas']
logBox.state(["readonly"])
logBox.grid(column=1,row=1,padx=10)

#Bind the combobox to a function
logBox.bind("<<ComboboxSelected>>",quant_select)

#Add a start button 
quant_sbutton = ttk.Button(quant_content,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton')
quant_sbutton.grid(column=0,row=2,pady=20,padx=20,columnspan=2)

#Bind the start button to a function
quant_sbutton.bind("<Button-1>",runQuant)

#var = ""
#togglebutton = ttk.Checkbutton(root, text='Switch', style='Switch',variable=var)
#togglebutton.grid(row=3,column=0)

#Main loop
root.mainloop()



