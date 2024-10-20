#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

SCRIPT FOR SIMPLIFYING ANALYSIS WORKFLOW

Julia Hancock
Started 01-04-2024

"""

""" PACKAGES """
print("[__main__] Loading packages...")
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter.font as tkFont
import os
import subprocess
import sys
from PIL import Image, ImageTk
from datetime import datetime
import importlib.util

""" LOCAL PACKAGES """
print("[__main__] Importing local packages...")
#Get current file absolute directory
file_dir = os.path.dirname(os.path.abspath(__file__))
#Get absolute directories for subpackages
subpack_dir = {'Handle':os.path.join(file_dir,'Handle','__init__.py'),
               'Manual':os.path.join(file_dir,'Manual','__init__.py'),
               'Match':os.path.join(file_dir,'Match','__init__.py'),
               'Quant':os.path.join(file_dir,'Quant','__init__.py')}

#Define function to import from path
def import_from_path(module_name,path):
    #Define spec
    spec = importlib.util.spec_from_file_location(module_name,path)
    #Define module
    module = importlib.util.module_from_spec(spec)
    #Expand sys.modules dict
    sys.modules[module_name] = module
    #Load module
    spec.loader.exec_module(module)
    return module

#Import all local packages
hd = import_from_path("hd",subpack_dir['Handle'])
mn = import_from_path("mn",subpack_dir['Manual'])
qt = import_from_path("qt",subpack_dir['Quant'])
mt = import_from_path("mt",subpack_dir['Match'])

""" PARAMETERS """
print("[__main__] Defining parameters...")
version = "0.3.0"
__version__ = "0.3.0"

""" UI FUNCTION """

def runUI():

    """ DIRECTORIES """
    print("[__main__] Defining directories...")
    print("[__main__] Using Handle package...")
    #Get directories from handling script
    directories = hd.handle(os.path.dirname(os.path.abspath(__file__)))
    #Unpack directories
    #Primary files directory
    files = directories['files']
    #Resources directory
    RE_Dir = directories['resources']
    #Theme directory
    theme_Dir = directories['theme']
    #Response factor directory
    RF_Dir = directories['rf']
    #Data directory
    DF_Dir = directories['data']
    #Images directory
    img_Dir = directories['images']
    #AutoFpmMatch directory + file
    afm_Dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'AutoFpmMatch.py')
    #AutoQuantification directory + file
    aq_Dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'AutoQuantification.py')
    
    """ DATA SEARCH """
    print("[__main__] Searching for valid data files...")
    #Get a list of all available sample data directories (excluding "old") in the data files directory
    sampleList = [f.name for f in os.scandir(DF_Dir) if f.is_dir() if f.name != "old"]
      
    """ FUNCTIONS """
    print("[__main__] Defining functions...")
    #Function for setting up the UI
    def uiSetup(theme_Dir):
        
        #Initialize UI window
        root = ThemedTk(theme='adapta')
    
        # Import the tcl file with the tk.call method
        root.tk.call('source', theme_Dir)
    
        # Set the theme with the theme_use method
        style = ttk.Style(root)
        style.theme_use('forest-light')
        #Set up style button font
        style.configure('QuantButton.TButton',font=('TKDefaultFont',16))
        #Set up style accent button font
        style.configure('Accent.TButton',font=('TKDefaultFont',16))
        #Set up labelframe font
        style.configure('QuantLabelframe.TLabelframe.Label',font=('TKDefaultFont',16))
    
        root.geometry("1090x560")
        root.title("ChromaQuant – Quantification Made Easy")
        root.resizable(0,0)
    
        #style.theme_use('forest')
        #Configure the grid
        root.columnconfigure(0,weight=2)
        root.columnconfigure(1,weight=2)
        root.columnconfigure(2,weight=2)
        root.columnconfigure(3,weight=2)
    
        #Create a main frame
        mainframe = ttk.Frame(root)
        mainframe.grid(column=0,row=0)
        
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
    
    #Function for running method functions
    def runProcess(sname,pythonFun,varList):
        """
        Function that runs an external main function
        Parameters
        ----------
        sname : String
            Name of sample to be analyzed.
        pythonFun : Function
            Function to be run.
        varList : List
            List of reformatted variables to be passed to the function.
    
        Returns
        -------
        None.
    
        """
        #Start time for execution time
        exec_start = datetime.now()
        #Insert sname at the beginning of the variables list
        varList.insert(0,sname)
        #Run the method function
        pythonFun(*varList)
        #End time for execution time
        exec_end = datetime.now()
        #Execution time
        exec_time = (exec_end-exec_start).total_seconds()*10**3
        print("Time to execute: {:.03f}ms".format(exec_time))
        print("Program complete")
        
        return None
    
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
                A list containing two lists, the first containing the variable options and the second containing reformatted values.
    
            Returns
            -------
            var_final : STRING
                The final, reformatted variable.
    
            """
            
            #Set default value of reformatted value
            var_final = "N/A"
            
            #Get the length of the variable option list
            listLength = len(ifTF_list[0])
            
            #For every entry in the variable option list...
            for i in range(listLength):
                
                #If the variable is equal to the ith variable option...
                if var_initial == ifTF_list[0][i]:
                    #Assign the variable to the first reformatted value
                    var_final = ifTF_list[1][i]
                #Otherwise, pass
                else:
                    pass
    
            return var_final
        
        #A dictionary containing the ifTF_lists for every passed variable
        ifTF_Dict = {'specLabTF':[[1,0],['True','False']],'sphase':[['Gas','Liquid'],['G','L']],'model':[['First order (linear)','Third order','Retention time'],['F','T','R']]}
        
        #A dictionary of all passed variables excluding sname
        passed_dict = {'sphase':sphase,'specLabTF':specLabTF,'model':model}
        
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
        if False in list(reformatBool_dict.values()) or sname == "":
            print("Cannot run FIDpMS script, one or more variables are not defined")
            pass
        
        #Otherwise, run the FIDpMS script
        else:
            print("Running FIDpMS script...")
            
            try:
                #Get list of reformatVar_dict values
                reformatVar_list = list(reformatVar_dict.values())
                print(reformatVar_list)
                #Append list with directories list
                reformatVar_list.append(directories)
                print(reformatVar_list)
                #Run subprocess
                runProcess(sname,mt.main_AutoFpmMatch,reformatVar_list)
                
            except subprocess.CalledProcessError as e:
                print(f'Command {e.cmd} failed with error {e.returncode}')
        
        return None
    
    #Function for running quant script
    def runQuant(sname,quantphases):
    
        print("User selected sample name {0} with phase(s) {1}".format(sname,quantphases))
        #If any of the required fields are empty, pass
        if sname == "" or quantphases == "":
            print("User did not enter a value for at least one required argument, canceling script run")
            pass
        #Otherwise, run the FIDpMS script
        else:
            print("Running Quantification script...")
            
            try:
                #Run subprocess
                runProcess(sname,qt.main_AutoQuantification,[quantphases,directories])
                
            except subprocess.CalledProcessError as e:
                print(f'Command {e.cmd} failed with error {e.returncode}')
        
        return None
    
    """ CODE """
    print("[__main__] Initializing UI mainframe...")
    #Run the UI setup
    root, mainframe = uiSetup(theme_Dir)
    
    #Create font objects
    title_font = tkFont.Font(size=18)   #Title font
        
    #IMAGE AND TITLE
    #Add a frame for the logo and title/sample info
    topFrame = ttk.Frame(mainframe)
    topFrame.grid(column=0,row=0,sticky='w',padx=(350,0))
    
    #Add a frame for the ChromaQuant logo
    logoFrame = ttk.Frame(topFrame)
    logoFrame.grid(column=0,row=0)
    
    #Add a frame for the title text and sample selection
    tsFrame = ttk.Frame(topFrame)
    tsFrame.grid(column=1,row=0)
    
    #Add title text
    tk.Label(tsFrame,text="ChromaQuant v"+version,font=title_font).grid(column=0,row=0,pady=10,padx=10)
    
    #Add an image for the ChromaQuant logo
    #Load the image
    #image = tk.PhotoImage(file=img_Dir+'ChromaQuantIcon.png')
    image_i = Image.open(os.path.join(img_Dir,'ChromaQuantIcon.png'))
    #Resize the image
    resize_image = image_i.resize((100,100))
    #Redefine the image
    image = ImageTk.PhotoImage(resize_image)
    #Add the image to a label
    image_label = tk.Label(logoFrame, image=image)
    image_label.grid(column=0,row=0,pady=10,padx=10)
    
    #SAMPLE SELECTION
    #Add a frame for selecting the sample
    sampleFrame = ttk.Frame(tsFrame)
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
    
    #WIDGET FRAME
    #Add a frame for the fidpms and quantification widgets
    widgetFrame = ttk.Frame(mainframe)
    widgetFrame.grid(column=0,row=1)
    
    #FIDPMS WIDGET
    #Add a frame
    fidpms_content = ttk.LabelFrame(widgetFrame,text='Peak Matching',style='QuantLabelframe.TLabelframe')
    fidpms_content.grid(column=0,row=0,pady=10,padx=10)
    
    #Add text to the top of the frame
    tk.Label(fidpms_content,text='Please enter all information').grid(column=0,row=0,columnspan=4,padx=20)
    
    #Set up a radiobutton for selecting liquid or gas
    tk.Label(fidpms_content,text='Please select the sample type:').grid(column=0,row=1,padx=10,pady=20,sticky='e')
    fpmVar = tk.StringVar()
    Liquid = ttk.Radiobutton(fidpms_content,text='Liquid',variable=fpmVar,value="Liquid",command=fidpms_select)
    Gas = ttk.Radiobutton(fidpms_content,text='Gas',variable=fpmVar,value="Gas",command=fidpms_select)
    Liquid.grid(column=1,row=1,padx=1,sticky='w')
    Gas.grid(column=2,row=1,padx=1,sticky='w')
    
    #Initially start with liquid selected
    fpmVar.set('Liquid')
    
    #Set up a radiobutton for selecting the model type
    tk.Label(fidpms_content,text='Please select the desired matching fit model:').grid(column=0,row=2,padx=10,pady=20,sticky='e')
    fpmMVar = tk.StringVar()
    third = ttk.Radiobutton(fidpms_content,text='Third order',variable=fpmMVar,value='Third order',command=fidpms_select_model)
    first = ttk.Radiobutton(fidpms_content,text='First order (linear)',variable=fpmMVar,value='First order (linear)',command=fidpms_select_model)
    rt = ttk.Radiobutton(fidpms_content,text='Retention time',variable=fpmMVar,value='Retention time',command=fidpms_select_model)
    third.grid(column=1,row=2,padx=1,sticky='w')
    first.grid(column=2,row=2,padx=1,sticky='w')
    rt.grid(column=3,row=2,padx=1,sticky='w')
    
    #Initially start with first order selected and third order disabled
    fpmMVar.set('First order (linear')
    third.config(state=tk.DISABLED)
    
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
    quant_content = ttk.LabelFrame(widgetFrame,text='Quantification',style='QuantLabelframe.TLabelframe')
    quant_content.grid(column=1,row=0,pady=10,padx=10,sticky="n")
    
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
    quant_sbutton = ttk.Button(quant_content,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton',command=lambda: runQuant(sampleVar.get(),logVar.get()))
    quant_sbutton.grid(column=0,row=2,pady=20,padx=20,columnspan=2)
    
    #Bind the start button to a function
    #quant_sbutton.bind("<Button-1>",runQuant)
    
    #var = ""
    #togglebutton = ttk.Checkbutton(root, text='Switch', style='Switch',variable=var)
    #togglebutton.grid(row=3,column=0)
    
    #Main loop
    root.mainloop()
    
    #End of runUI function
    return None

""" RUN MAIN FUNCTION """
print("[__main__] Starting UI...")
if __name__ == "__main__":
	runUI()

