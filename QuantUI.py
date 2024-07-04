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

version = "1.1"

""" DIRECTORIES """
#Main directory
cwd = os.getcwd()+"/"
#Data directory
DF_Dir = cwd+"data/"
#Response factors directory
RF_Dir = cwd+"response-factors/"
#Resources directory
RE_Dir = cwd+"resources/"
#Theme directory
theme_Dir = RE_Dir+"forest/forest-light.tcl"

""" DATA SEARCH """

#Get a list of all available sample data directories (excluding "old") in the data files directory
sampleList = [f.name for f in os.scandir(DF_Dir) if f.is_dir() if f.name != "old"]

""" CLASSES """
"""
class mainUI():
    def __init__(self):
        
        #Function for sample selection combobox
        def on_select(self):
            
           sname = sampleBox.get()
           print("User selected "+sampleBox.get())
           return sname

        #Function for fidpms phase selection combobox
        def fidpms_select(self):
            
            sphase = fpmVar.get()
            print("User selected " + sphase)
            
            return sphase

        #Function for model selection combobox
        def fidpms_select_model(self):
            
            model = fpmMVar.get()
            print("User selected " + model)
            
            return model
            
        #Function for fidpms speculative labeling combobox
        def fidpms_select2(self):
            
            specLabTF = fpm2Var.get()
            print("User selected " + specLabTF)

            return specLabTF

        #Function for quant phase selection combobox
        def quant_select(self):
            
            global quantphases
            quantphases = logBox.get()

        
        def uiSetup():
            
            #Initialize UI window
            self.root = ThemedTk(theme='adapta')
    
            # Import the tcl file with the tk.call method
            self.root.tk.call('source', theme_Dir)  # Put here the path of your theme file
    
            # Set the theme with the theme_use method
            self.style = ttk.Style(self.root)
            self.style.theme_use('forest-light')  # Theme files create a ttk theme, here you can put its name
            #Set up style button font
            self.style.configure('QuantButton.TButton',font=('TKDefaultFont',16))
            #Set up style accent button font
            self.style.configure('Accent.TButton',font=('TKDefaultFont',16))
            #Set up labelframe font
            self.style.configure('QuantLabelframe.TLabelframe.Label',font=('TKDefaultFont',16))
    
            self.root.geometry("1024x980")
            self.root.title("AutoQuantUI – Quantification Made Easy")
            self.root.resizable(0,0)
    
            #Create font objects
            self.title_font = tkFont.Font(size=18)   #Title font
    
            #style.theme_use('forest')
            #Configure the grid
            self.root.columnconfigure(0,weight=2)
            self.root.columnconfigure(1,weight=2)
            self.root.columnconfigure(2,weight=2)
            self.root.columnconfigure(3,weight=2)
    
            #Create a main frame
            self.mainframe = ttk.Frame(self.root)
            self.mainframe.grid(column=0,row=0)
    
            #Add title text
            tk.Label(self.mainframe,text="AutoQuant v"+version,font=self.title_font).grid(column=0,row=0,columnspan=4,pady=5)
            
            return self.root, self.mainframe
        
        #Initializing Widgets
        
        root, mainframe = uiSetup()
        #SAMPLE SELECTION
        #Add a frame for selecting the sample
        sampleFrame = ttk.Frame(mainframe)
        sampleFrame.grid(column=0,row=1,pady=10,padx=10)

        #Add text to the top of the sample frame
        tk.Label(sampleFrame,text='Select a sample to analyze:').grid(column=0,row=0)
        sampleVar = tk.StringVar()
        sampleBox = ttk.Combobox(sampleFrame,textvariable=sampleVar)
        sampleBox['values'] = sampleList
        sampleBox.state(["readonly"])
        sampleBox.grid(column=0,row=1)

        #Bind the sampleBox to a function
        sampleBox.bind("<<ComboboxSelected>>",on_select)

        #FIDPMS WIDGET
        #Add a frame
        fidpms_content = ttk.LabelFrame(mainframe,text='Peak Matching',style='QuantLabelframe.TLabelframe')
        fidpms_content.grid(column=0,row=2,pady=10,padx=10)
        fidpms_content.columnconfigure(0,weight=1)

        #Add text to the top of the frame
        tk.Label(fidpms_content,text='Please enter all information').grid(column=0,row=0,columnspan=4,padx=20)
        
        #Set up a radiobutton for selecting liquid or gas
        tk.Label(fidpms_content,text='Please select the sample type:').grid(column=0,row=1,padx=10,pady=20,sticky='e')
        fpmVar = tk.StringVar()
        Liquid = ttk.Radiobutton(fidpms_content,text='Liquid',variable=fpmVar,value="Liquid",command=fidpms_select)
        Gas = ttk.Radiobutton(fidpms_content,text='Gas',variable=fpmVar,value="Gas",command=fidpms_select)
        Liquid.grid(column=1,row=1,padx=1,sticky='w')
        Gas.grid(column=2,row=1,padx=1,sticky='w')
        
        #Set up a radiobutton for selecting the model type
        tk.Label(fidpms_content,text='Please select the desired matching fit model:').grid(column=0,row=2,padx=10,pady=20,sticky='e')
        fpmMVar = tk.StringVar()
        third = ttk.Radiobutton(fidpms_content,text='Third order',variable=fpmMVar,value="Third order",command=fidpms_select_model)
        first = ttk.Radiobutton(fidpms_content,text='First order (linear)',variable=fpmMVar,value="First order (linear)",command=fidpms_select_model)
        third.grid(column=1,row=2,padx=1,sticky='w')
        first.grid(column=2,row=2,padx=1,sticky='w')
        
        #Set up a checkbox for selecting whether or not to perform speculative labeling
        tk.Label(fidpms_content,text='Perform speculative labeling?').grid(column=0,row=3,padx=10,pady=20,sticky='e')
        fpm2Var = tk.IntVar()
        fpm2Box = tk.Checkbutton(fidpms_content,text='',variable=fpm2Var,onvalue=1,offvalue=0,command=fidpms_select2)
        fpm2Box.grid(column=1,row=3,padx=1,sticky='w')

        #Add a start button
        fidpms_sbutton = ttk.Button(fidpms_content,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton',command=lambda: runFIDpMS(sampleVar.get(),fpm2Var.get(),fpmVar.get(),fpmMVar.get()))
        fidpms_sbutton.grid(column=0,row=4,pady=20,padx=20,columnspan=2)

        #Bind the button to a function to run the appropriate script
        #fidpms_sbutton.bind("<Button-1>",runFIDpMS)


        #QUANT WIDGET
        #Add a frame
        quant_content = ttk.LabelFrame(mainframe,text='Quantification',style='QuantLabelframe.TLabelframe')
        quant_content.grid(column=1,row=2,pady=10,padx=10,sticky="n")
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
        
"""
  
""" FUNCTIONS """

#Function for setting up the UI
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

    root.geometry("1024x980")
    root.title("AutoQuantUI – Quantification Made Easy")
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
    tk.Label(mainframe,text="AutoQuant v"+version,font=title_font).grid(column=0,row=0,columnspan=4,pady=5)
    
    return root, mainframe
#Function for sample selection combobox
def on_select(event):
    
   sname = sampleBox.get()
   print("User selected "+sampleBox.get())
   return sname

#Function for fidpms phase selection combobox
def fidpms_select():
    
    sphase = fpmVar.get()
    print("User selected " + sphase)
    
    if sphase == "Liquid":
        #Set variable to first order
        fpmMVar.set('First order (linear)')
        #Disable third order
        third.config(state=tk.DISABLED)
    else:
        third.config(state=tk.NORMAL)
    
    return sphase

#Function for model selection combobox
def fidpms_select_model():
    
    model = fpmMVar.get()
    print("User selected " + model)
    
    return model
    
#Function for fidpms speculative labeling combobox
def fidpms_select2():
    
    specLabTF = fpm2Var.get()
    print("User selected " + specLabTF)

    return specLabTF

#Function for quant phase selection combobox
def quant_select(event):
    
    global quantphases
    quantphases = logBox.get


#Function for running FIDpMS script
def runFIDpMS(sname,specLabTF,sphase,model):
    """
    Parameters
    ----------
    sname : STRING
        Name of sample to be analyzed.
    specLabTF : STRING
        True/false string describing whether speculative labeling is to be performed.
    sphase : TYPE
        String describing whether liquid or gas is to be performed.
    model : TYPE
        String describing which model is to be performed.

    Returns
    -------
    NONE

    """
    
    #Function for reformatting provided variables
    def reformatVar(var_initial,ifTF_list):
        """
        Parameters
        ----------
        var_initial : STRING, BOOLEAN
            The initial variable to be reformatted.
        ifTF_list : LIST
            A list containing two lists, the first containing the boolean statements and the second containing reformatted values.

        Returns
        -------
        var_final : STRING
            The final, reformatted variable.

        """

        #If the initial variable is equal to the first boolean statement...
        if var_initial == ifTF_list[0][0]:
            #Assign the variable to the first reformatted value
            var_final = ifTF_list[1][0]
            
        #If the initial variable is equal to the second boolean statement...
        elif var_initial == ifTF_list[0][1]:
            #Assign the variable to the second reformatted value
            var_final = ifTF_list[1][1]
            
        #Otherwise, set var_final equal to "N/A"
        else:
            var_final = "N/A"
        
        return var_final
    
    #A dictionary containing the ifTF_lists for every passed variable
    ifTF_Dict = {'specLabTF':[[1,0],['True','False']],'sphase':[['Gas','Liquid'],['G','L']],'model':[['First order (linear)','Third order'],['F','T']]}
    
    #A dictionary of all passed variables excluding sname
    passed_dict = {'specLabTF':specLabTF,'sphase':sphase,'model':model}
    
    print("User selected sample name {0} with phase {2} and entered {1} for running speculative labeling. Modeling is {3}".format(sname,specLabTF,sphase,model))
    
    #A dictionary for all reformatted variables
    reformatVar_dict = {}
    
    #A dictionary of booleans describing whether or not values in reformatVar_dict are "N/A"
    reformatBool_dict = {}
    
    #Reformat all variables
    for i in passed_dict.keys():
        
        #Print reformatted variable name
        print("Reformatting " + i + "...")
        #Reformat variable, append to dictionary
        reformatVar_dict[i] = reformatVar(passed_dict[i],ifTF_Dict[i])
        #Print resulting reformatted value
        print("Variable has been reformatted to {0}".format(reformatVar_dict[i]))
        
        #Check if reformatted variable is equal to "N/A". If it is, assign False
        if reformatVar_dict[i] == "N/A":
            reformatBool_dict[i] = False
        #Otherwise, assign True
        else:
            reformatBool_dict[i] = True
    
    #If any of the required fields are empty, pass
    if False in list(reformatBool_dict.values()):
        print("Cannot run FIDpMS script, one or more variables are not defined")
        pass
    
    #Otherwise, run the FIDpMS script
    else:
        print("Running FIDpMS script...")
        
        try:
            #Get list of reformatVar_dict values
            reformatVar_list = list(reformatVar_dict.values())
            #Run the subprocess
            subprocess.run(['python','AutoFPMMatch.py',sname,reformatVar_list[1],reformatVar_list[0],reformatVar_list[2]], text=True, check=True)
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
sampleFrame.grid(column=0,row=1,pady=10,padx=10)

#Add text to the top of the sample frame
tk.Label(sampleFrame,text='Select a sample to analyze:').grid(column=0,row=0)
sampleVar = tk.StringVar()
sampleBox = ttk.Combobox(sampleFrame,textvariable=sampleVar)
sampleBox['values'] = sampleList
sampleBox.state(["readonly"])
sampleBox.grid(column=0,row=1)

#Bind the sampleBox to a function
sampleBox.bind("<<ComboboxSelected>>",on_select)

#FIDPMS WIDGET
#Add a frame
fidpms_content = ttk.LabelFrame(mainframe,text='Peak Matching',style='QuantLabelframe.TLabelframe')
fidpms_content.grid(column=0,row=2,pady=10,padx=10)
fidpms_content.columnconfigure(0,weight=1)

#Add text to the top of the frame
tk.Label(fidpms_content,text='Please enter all information').grid(column=0,row=0,columnspan=4,padx=20)

"""
#Set up a combobox for selecting liquid or gas
tk.Label(fidpms_content,text='Please select the sample type').grid(column=0,row=1,padx=10,pady=20)
fpmVar = tk.StringVar()
fpmBox = ttk.Combobox(fidpms_content,textvariable=fpmVar)
fpmBox['values'] = ['Liquid','Gas']
fpmBox.state(["readonly"])
fpmBox.grid(column=1,row=1,padx=10)

#Bind the combobox to a function
fpmBox.bind("<<ComboboxSelected>>",fidpms_select)
"""

#Set up a radiobutton for selecting liquid or gas
tk.Label(fidpms_content,text='Please select the sample type:').grid(column=0,row=1,padx=10,pady=20,sticky='e')
fpmVar = tk.StringVar()
Liquid = ttk.Radiobutton(fidpms_content,text='Liquid',variable=fpmVar,value="Liquid",command=fidpms_select)
Gas = ttk.Radiobutton(fidpms_content,text='Gas',variable=fpmVar,value="Gas",command=fidpms_select)
Liquid.grid(column=1,row=1,padx=1,sticky='w')
Gas.grid(column=2,row=1,padx=1,sticky='w')

#Initially start with liquid selected
fpmVar.set('Liquid')

"""
#Set up a combobox for selecting the fit model
tk.Label(fidpms_content,text='Please select the desired matching fit model:').grid(column=0,row=2,padx=0,pady=20)
fpmMVar = tk.StringVar()
fpmMBox = ttk.Combobox(fidpms_content,textvariable=fpmMVar)
fpmMBox['values'] = ['First order (linear)','Third order']
fpmMBox.state(["readonly"])
fpmMBox.grid(column=1,row=2,padx=1)

#Bind the combobox to a function
fpmMBox.bind("<<ComboboxSelected>>",fidpms_select_model)
"""

#Set up a radiobutton for selecting the model type
tk.Label(fidpms_content,text='Please select the desired matching fit model:').grid(column=0,row=2,padx=10,pady=20,sticky='e')
fpmMVar = tk.StringVar()
third = ttk.Radiobutton(fidpms_content,text='Third order',variable=fpmMVar,value="Third order",command=fidpms_select_model)
first = ttk.Radiobutton(fidpms_content,text='First order (linear)',variable=fpmMVar,value="First order (linear)",command=fidpms_select_model)
third.grid(column=1,row=2,padx=1,sticky='w')
first.grid(column=2,row=2,padx=1,sticky='w')

#Initially start with first order selected and third order disabled

fpmMVar.set('First order (linear')
third.config(state=tk.DISABLED)

"""
#Set up a combobox for selecting whether or not to perform speculative labeling
tk.Label(fidpms_content,text='Perform speculative labeling?').grid(column=0,row=3,padx=0,pady=20)
fpm2Var = tk.StringVar()
fpm2Box = ttk.Combobox(fidpms_content,textvariable=fpm2Var)
fpm2Box['values'] = ['Yes','No']
fpm2Box.state(["readonly"])
fpm2Box.grid(column=1,row=3,padx=1)

#Bind the combobox to a function
fpm2Box.bind("<<ComboboxSelected>>",fidpms_select2)
"""

#Set up a checkbox for selecting whether or not to perform speculative labeling
tk.Label(fidpms_content,text='Perform speculative labeling?').grid(column=0,row=3,padx=10,pady=20,sticky='e')
fpm2Var = tk.IntVar()
fpm2Box = tk.Checkbutton(fidpms_content,text='',variable=fpm2Var,onvalue=1,offvalue=0,command=fidpms_select2)
fpm2Box.grid(column=1,row=3,padx=1,sticky='w')

#Add a start button
fidpms_sbutton = ttk.Button(fidpms_content,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton',command=lambda: runFIDpMS(sampleVar.get(),fpm2Var.get(),fpmVar.get(),fpmMVar.get()))
fidpms_sbutton.grid(column=0,row=4,pady=20,padx=20,columnspan=2)

#DISABLING SPECULATIVE LABELING
fpm2Box.config(state=tk.DISABLED)

#Bind the button to a function to run the appropriate script
#fidpms_sbutton.bind("<Button-1>",runFIDpMS)


#QUANT WIDGET
#Add a frame
quant_content = ttk.LabelFrame(mainframe,text='Quantification',style='QuantLabelframe.TLabelframe')
quant_content.grid(column=1,row=2,pady=10,padx=10,sticky="n")
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

