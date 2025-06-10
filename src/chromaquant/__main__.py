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

SCRIPT FOR SIMPLIFYING ANALYSIS WORKFLOW

Julia Hancock
Started 12-10-2024

"""

""" PACKAGES """
print("[__main__] Loading packages...")
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
import tkinter.font as tkFont
import os
import sys
from PIL import Image, ImageTk
from datetime import datetime
import importlib.util
import threading
import time
import json

""" LOCAL PACKAGES """
print("[__main__] Importing local packages...")
#Get current file absolute directory
file_dir = os.path.dirname(os.path.abspath(__file__))
#Get absolute directories for subpackages
subpack_dir = {'Handle':os.path.join(file_dir,'Handle','__init__.py'),
               'Manual':os.path.join(file_dir,'Manual','__init__.py'),
               'Match':os.path.join(file_dir,'Match','__init__.py'),
               'Quant':os.path.join(file_dir,'Quant','__init__.py'),
               'UAPP':os.path.join(file_dir,'UAPP','__init__.py'),
               'Hydro':os.path.join(file_dir,'Hydro','__init__.py')}

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
ua = import_from_path("ua",subpack_dir['UAPP'])
#hy = import_from_path("hy",subpack_dir['Hydro'])

""" PARAMETERS """
print("[__main__] Defining parameters...")
__version__ = "0.4.0"
version = "0.4.0"

""" RUNUI FUNCTION """

#Function to run the UI
def runUI(file_dir):

    """ DIRECTORIES """
    print("[__main__] Defining directories...")

    print("[__main__] Validating directories...")
    #Check and update app and documents directories
    props = hd.updateDirectories(file_dir)

    print("[__main__] Unpacking directories...")
    #Get directories from handling script
    directories = hd.handle(props)

    """ DATA SEARCH """
    print("[__main__] Searching for valid data files...")
    #Get a list of all available sample data directories (excluding "old") in the data files directory
    sampleList = [f.name for f in os.scandir(directories['data']) if f.is_dir() if f.name != "old"]

    """ CODE """
    #Define ChromaQuantUI as class
    class chromaUI:

        #Key variables = sampleVar, fpm_typevar, fpm_modelvar, quant_typevar, quant_modelvar, hydro_typevar
        #Initialization function – master here will be our root widget
        def __init__(self, master, directories):

            self.master = master
            self.directories = directories

            #ANALYSIS CONFIGURATION
            print("[__main__] Interpreting analysis configuration...")
            #Read analysis configuration file
            with open(os.path.join(self.directories['resources'],'analysis-config.json')) as f:
                self.analysis_config = json.load(f)

            #Extract analysis configuration info
            #File suffixes to add to form data filenames
            self.file_suffix_list = [i[0] for i in list(self.analysis_config["file-suffix"].values())]

            #Standard padding
            self.std_padx = 10
            self.std_pady = 10

            #Padding for widgets/widget rows
            self.widget_padx = 20
            self.widget_pady = 20

            #Initialize user variable dictionary
            self.var_dict = {}
            #Initialize user variable entries
            self.var_dict['sampleVar'] = tk.StringVar()
            self.var_dict['fpm_typevar'] = tk.StringVar()
            self.var_dict['fpm_modelvar'] = tk.StringVar()
            self.var_dict['quant_typevar'] = tk.StringVar()
            self.var_dict['quant_modelvar'] = tk.StringVar()
            self.var_dict['hydro_typevar'] = tk.StringVar()
            self.var_dict['hydro_matchvar'] = tk.StringVar()

            #Initialize list of variables to have an anonymous printing function
            self.varSelect_list = ['sampleVar','fpm_typevar','fpm_modelvar','quant_modelvar','hydro_typevar','hydro_matchvar']

            #Initialize radiobutton object dictionary
            self.radio_dict = {}

            #Setup UI
            self.setupUI()

            #Create font objects
            self.title_font = tkFont.Font(size=18,weight='bold')   #Title font
            
            #SETUP SELECT FUNCTIONS
            self.setupVarSelect()

            #IMAGE AND TITLE
            #Add a frame for the logo and title/sample info
            self.topFrame = ttk.Frame(self.mainframe)
            self.topFrame.grid(column=0,row=0,sticky='WE')
            self.topFrame.grid_columnconfigure((0,3),weight=1)
            self.setupTitle()

            #WIDGETS
            #Add a frame for the first row of widgets
            self.rowoneFrame = ttk.Frame(self.mainframe)
            self.rowoneFrame.grid(column=0,row=1,sticky='WE')
            self.rowoneFrame.grid_columnconfigure((0,4),weight=1)

            #Add a frame for the second row of widgets
            self.rowtwoFrame = ttk.Frame(self.mainframe)
            self.rowtwoFrame.grid(column=0,row=2,sticky='WE')
            self.rowtwoFrame.grid_columnconfigure((0,4),weight=1)

            #FILE TRACKING
            #Add a frame for tracking data files
            self.trackFrame = ttk.LabelFrame(self.rowoneFrame,text='File Tracking',style='QuantLabelframe.TLabelframe')
            self.trackFrame.grid(column=1,row=0,sticky='NSWE',padx=self.widget_padx,pady=self.widget_pady)
            self.setupFileTrack()

            #UNKNOWNS ANALYSIS POSTPROCESS
            #Add a frame for the UA_UPP script
            self.uppFrame = ttk.LabelFrame(self.rowoneFrame,text='Unknowns Analysis Postprocessing',style='QuantLabelframe.TLabelframe')
            self.uppFrame.grid(column=2,row=0,sticky='NSWE',padx=(0,self.widget_padx),pady=self.widget_pady)
            self.setupUPP()
            #padx=self.widget_padx,pady=self.widget_pady
            
            #FIDpMS MATCHING
            #Add a frame for the main matching script
            self.matchFrame = ttk.LabelFrame(self.rowoneFrame,text='Peak Matching',style='QuantLabelframe.TLabelframe')
            self.matchFrame.grid(column=3,row=0,sticky='NSWE',padx=(0,self.widget_padx),pady=self.widget_pady)
            self.setupMatch()

            #QUANTIFICATION
            #Add a frame for the main quantification script
            self.quantFrame = ttk.LabelFrame(self.rowtwoFrame,text='Quantification',style='QuantLabelframe.TLabelframe')
            self.quantFrame.grid(column=1,row=0,sticky='NSWE',padx=self.widget_padx,pady=(0,self.widget_pady))
            self.setupQuant()

            #HYDROUI
            #Add a frame for the hydroUI script
            self.hydroFrame = ttk.LabelFrame(self.rowtwoFrame,text='HydroUI (WIP)',style='QuantLabelframe.TLabelframe')
            self.hydroFrame.grid(column=2,row=0,sticky='NSWE',padx=(0,self.widget_padx),pady=(0,self.widget_pady))
            self.setupHydro()

        def default(self):
            print("[__main__][TEST] Testing message")
        
        def setupUI(self):
        
            # Import the tcl file with the tk.call method
            self.master.tk.call('source', self.directories['theme'])
        
            # Set the theme with the theme_use method
            style = ttk.Style(root)
            style.theme_use('forest-light')
            #Set up style button font
            style.configure('QuantButton.TButton',font=('Arial',16))
            #Set up style accent button font
            style.configure('Accent.TButton',font=('Arial',16))
            #Set up labelframe font
            style.configure('QuantLabelframe.TLabelframe.Label',font=('Arial',16))
            #Set up labelframe border
            style.configure('QuantLabelframe.TLabelframe',borderwidth=5,bordercolor='red')
            #Set up file tracking text font
            self.fileTrackFont = tkFont.Font(size=14)
        
            #root.geometry("890x1000")
            root.title("ChromaQuant – Quantification Made Easy")
        
            #Create a main frame
            self.mainframe = ttk.Frame(root)
            self.mainframe.grid(column=0,row=0)

        def setupTitle(self):

            #Add a frame for the ChromaQuant logo
            self.logoFrame = ttk.Frame(self.topFrame)
            self.logoFrame.grid(column=1,row=0,sticky='WE')
            
            #Add a frame for the title text and sample selection
            self.tsFrame = ttk.Frame(self.topFrame)
            self.tsFrame.grid(column=2,row=0,sticky='E')

            #Add title text
            tk.Label(self.tsFrame,text="ChromaQuant v"+version,font=self.title_font)\
                .grid(column=0,row=0,pady=self.std_pady,padx=self.std_padx)
            
            #Add an image for the ChromaQuant logo
            #Load the image
            self.image_i = Image.open(os.path.join(self.directories['images'],'ChromaQuantIcon.png'))
            #Resize the image
            self.resize_image = self.image_i.resize((100,100))
            #Redefine the image
            self.image = ImageTk.PhotoImage(self.resize_image)
            #Add the image to a label
            image_label = tk.Label(self.logoFrame, image=self.image)
            image_label.grid(column=0,row=0,pady=10,padx=10)

            #Add a frame for selecting the sample
            sampleFrame = ttk.Frame(self.tsFrame)
            sampleFrame.grid(column=0,row=1,pady=10,padx=10)
            
            #Add text to the top of the sample frame
            tk.Label(sampleFrame,text='Select a sample to analyze:').grid(column=0,row=0)
            self.var_dict['sampleVar'] = tk.StringVar()
            self.sampleBox = ttk.Combobox(sampleFrame,textvariable=self.var_dict['sampleVar'])
            self.sampleBox['values'] = sampleList
            self.sampleBox.state(["readonly"])
            self.sampleBox.grid(column=0,row=1)
        
            #Bind the sampleBox to a function
            self.sampleBox.bind("<<ComboboxSelected>>",self.sampleSelect)
        
        def setupFileTrack(self):

            #Create text window, place in grid
            self.fileTrack_Text = tk.Text(self.trackFrame, height=12, width=20, fg='black', font=self.fileTrackFont)
            self.fileTrack_Text.grid(column=0,row=0,padx=20,pady=10,sticky='NSWE')
            #Set text config to NORMAL
            self.fileTrack_Text.config(state=tk.NORMAL)
            #Configure text options
            #Option for default text
            self.fileTrack_Text.tag_config('default', background="white", foreground="black")
            #Option for present file
            self.fileTrack_Text.tag_config('true', background="white", foreground='green')
            #Option for file not found
            self.fileTrack_Text.tag_config('false', background="white", foreground='red')

            #Create default options
            for i in self.file_suffix_list:
                self.fileTrack_Text.insert(tk.END,"\n{0}".format(i),'default')
            
        def updateFileTrack(self):

            #Delete all text in file tracking widget
            self.fileTrack_Text.delete(1.0,tk.END)

            #Get list of files currently in data and raw data directory
            self.rawDataFiles = [f.lower() for f in os.listdir(directories['raw']) if os.path.isfile(os.path.join(directories['raw'],f))]
            self.dataFiles = [f.lower() for f in os.listdir(directories['sample']) if os.path.isfile(os.path.join(directories['sample'],f))]
            
            #Loop through the data files to search for everything but the INFO file (last index)
            for i in self.file_suffix_list[:-1]:

                #If given file exists in list, color green
                if (self.sname+i).lower() in self.rawDataFiles:
                    self.fileTrack_Text.insert(tk.END,"\n{0}".format(i),'true')

                #Otherwise, color red
                else:
                    self.fileTrack_Text.insert(tk.END,"\n{0}".format(i),'false')

            #If last data file (INFO) exists in data files directory, color green
            if (self.sname+self.file_suffix_list[-1]).lower() in self.dataFiles:
                    self.fileTrack_Text.insert(tk.END,"\n{0}".format(self.file_suffix_list[-1]),'true')
            
            #Otherwise, color red
            else:
                    self.fileTrack_Text.insert(tk.END,"\n{0}".format(self.file_suffix_list[-1]),'false')

            print("[__main__] File tracking results updated...")

        def setupUPP(self):

            #Add start button
            self.setupStartButton(self.uppFrame,[0,0],[20,20],1,self.runUPP)

        def setupMatch(self):
            
            #Add a radiobutton set for selecting sample type
            self.radio_dict['fpm_typevar'] = self.setupRadioButton(self.matchFrame,'Please select the sample type:',[0,1],[20,20],1,'fpm_typevar',{'Liquid':'L','Gas':'G'},self.select_dict['fpm_typevar'],'L')
            #Add a radiobutton set for selecting match model
            self.radio_dict['fpm_modelvar'] = self.setupRadioButton(self.matchFrame,'Please select the desired matching fit model:',[0,2],[20,20],1,'fpm_modelvar',{'Retention\nTime':'R','Polynomial':'P'},self.select_dict['fpm_modelvar'],'R')
            #Add start button
            self.setupStartButton(self.matchFrame,[0,3],[20,20],4,self.runMatch)

        def setupQuant(self):
            
            #Add a radiobutton set for selecting sample type
            self.radio_dict['quant_typevar'] = self.setupRadioButton(self.quantFrame,'Which components are present in the sample?',[0,1],[20,20],1,'quant_typevar',{'Liquid\nOnly':'L','Gas\nOnly':'G','Liquid\nand Gas':'LG'},self.quant_typevarSelect,'L')
            
            #Add a radiobutton set for selecting the gas quantification method
            self.radio_dict['quant_modelvar'] = self.setupRadioButton(self.quantFrame,'Which method should be used to quantify gas phase products?',[0,2],[20,0],1,'quant_modelvar',{'CO2\nVolume':'C','Scale\nFactor':'S','Internal\nStandard':'I'},self.select_dict['quant_modelvar'],'Disabled')
            
            #Add start button
            self.setupStartButton(self.quantFrame,[0,3],[20,20],4,self.runQuant)

        def setupHydro(self):
            
            #Add a radiobutton set for selecting sample type
            self.radio_dict['hydro_typevar'] = self.setupRadioButton(self.hydroFrame,'Which phase to analyze?',[0,1],[20,20],1,'hydro_typevar',{'Liquid':'L','Gas':'G'},self.select_dict['hydro_typevar'],'L')
            #Add a radiobutton set for selecting sample type
            self.radio_dict['hydro_matchvar'] = self.setupRadioButton(self.hydroFrame,'Display FID and MS matches?',[0,2],[20,20],1,'hydro_matchvar',{'Yes':'T','No':'F'},self.select_dict['hydro_matchvar'],'F')
            #Add start button
            self.setupStartButton(self.hydroFrame,[0,3],[20,20],4,self.runHydro)

        def setupStartButton(self,frame,placement,pad,columnspan,function):

            #Add a start button
            ttk.Button(frame,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton',command=function)\
                .grid(column=placement[0],row=placement[1],padx=pad[0],pady=pad[1],columnspan=columnspan)

        def setupRadioButton(self,frame,label_text,placement,pad,columnspan,var_name,option_val_dict,function,init_state='Option Blank'):
            
            #placement = [column,row]
            #pad = [padx,pady]
            #var_dict = {'var_1':tk.StringVar(),...}
            #var_name = 'var_1'
            #text_val_dict = {'option_1':'value_1',...}

            #Set up a radiobutton for selecting liquid or gas
            #Add a label
            tk.Label(frame,text=label_text).grid(column=placement[0],row=placement[1],padx=pad[0],pady=pad[1],columnspan=columnspan,sticky='e')

            #Define current column as column to the right of label
            current_col = placement[0] + 1
            #Define radiobutton padding loop iterable
            current_pad = 0
            #Define list to iterate through for radiobutton padding
            radiopad = [(10,10) for i in range(len(option_val_dict))]
            radiopad[-1] = (10,20)

            #Define list of radiobutton objects
            dict_radiobutton = {i:0 for i in option_val_dict}

            #For every option in the option-value dictionary, add a radiobutton (iterate over columns)
            for option in option_val_dict:

                #Store the radiobutton object
                dict_radiobutton[option] = ttk.Radiobutton(frame , text=option , variable=self.var_dict[var_name] , value=option_val_dict[option] , command=function)
                dict_radiobutton[option].grid(column=current_col , row=placement[1] , padx=radiopad[current_pad] , sticky='w')
                
                #Iterate current column and radio padding list
                current_col += 1
                current_pad += 1

            #Select the initial radiobutton state based on the init_state argument
            #If init_state is 'Option Blank', select the first radiobutton
            if init_state == 'Option Blank':
                self.var_dict[var_name].set(next(iter(option_val_dict.values())))

            #If init_state is 'Disabled', set the radiobuttons to be disabled
            elif init_state == 'Disabled':
                for option in option_val_dict:
                    dict_radiobutton[option].config(state=tk.DISABLED)

            #Otherwise, if the init_state does not have a counterpart in the values of the option_val_dict, select the first radiobutton
            elif init_state not in option_val_dict.values():
                self.var_dict[var_name].set(next(iter(option_val_dict.values())))
            
            #Otherwise, select the specified radiobutton
            else:
                self.var_dict[var_name].set(init_state)

            return dict_radiobutton
        

        def sampleSelect(self,event):

            self.sname = self.sampleBox.get()

            print("[__main__] User selected " + self.sname)

            print("[__main__] Getting sample directories...")

            #Sample directory
            self.directories['sample'] = os.path.join(self.directories['data'],self.sname)

            #Data file log directory
            self.directories['log'] = os.path.join(self.directories['sample'],'log')

            #Data file breakdowns directory
            self.directories['break'] = os.path.join(self.directories['sample'],'breakdowns')

            #Raw data file directory
            self.directories['raw'] = os.path.join(self.directories['sample'],'raw data')

            print("[__main__] Checking files...")
            self.updateFileTrack()

            return self.sname

        #Function for setting up anonymous varaible select functions for printing messages
        def setupVarSelect(self):
            
            #Predefine dictionary for selection functions
            self.select_dict = {}

            #For every variable...
            for i in self.var_dict:

                #If variable is listed in the anonymous variable list...
                if i in self.varSelect_list:
                    #Define lambda function using default argument for user selection message
                    self.select_dict[i] = lambda i=i: print("[__main__] User Selected " + self.var_dict[i].get() + " for " + i)
                
                #Otherwise, pass
                else:
                    pass

            return None

        #Function for quant_typevar selection
        def quant_typevarSelect(self):

            #If the phase selected is either gas or both liquid and gas...
            if self.var_dict['quant_typevar'].get() == 'G' or self.var_dict['quant_typevar'].get() == 'LG':
                #Enable all radiobuttons
                for radiobutton in self.radio_dict['quant_modelvar']:
                    self.radio_dict['quant_modelvar'][radiobutton].config(state=tk.NORMAL)

            #Otherwise, disable all radiobuttons
            else:
                #Disable all radiobuttons
                for radiobutton in self.radio_dict['quant_modelvar']:
                    print(radiobutton)
                    self.radio_dict['quant_modelvar'][radiobutton].config(state=tk.DISABLED)
                
                #Set quant_modelvar to none
                self.var_dict['quant_modelvar'].set(None)

            print("[__main__] User Selected " + self.var_dict['quant_typevar'].get() + " for quant_typevar")

            return None

        #Function for 
        def runUPP(self):
            #Function for running the UPP function
            print("[__main__] Running Unknowns Analysis Postprocessing...")
            ua.mainUAPP(self.var_dict['sampleVar'].get())
            print("[__main__] UAPP complete")
            return None
        
        def runMatch(self):
            #Function for running the match function
            print("[__main__] Running FID and MS matching...")
            mt.mainMatch(self.var_dict['sampleVar'].get(), self.var_dict['fpm_typevar'].get(),self.var_dict['fpm_modelvar'].get())
            print("[__main__] Matching complete")
            return None
        
        def runQuant(self):
            #Function for running the quantification function
            print("[__main__] Running quantification...")
            qt.mainQuant(self.var_dict['sampleVar'].get(), self.var_dict['quant_typevar'].get(), self.var_dict['quant_modelvar'].get())
            print("[__main__] Quantification complete")
            return None
        
        def runHydro(self):

            #Function for running the hydroUI function
            print("[__main__] Defining HydroUI application...")
            """ COMMENT OUT FOR NOW, LAGGY
            self.app = hy.mainHydro(self.var_dict['sampleVar'].get(), self.var_dict['hydro_typevar'].get(), self.var_dict['hydro_matchvar'].get())
            print("[__main__] Application defined, running...")
            if __name__ == "__main__":
                #Define a thread and set as daemon – SCRIPT WILL CONTINUE TO RUN UNTIL CHROMAUI CLOSED
                hydroThread = threading.Thread(target=lambda: self.app.run(debug=True, use_reloader=False))
                hydroThread.daemon = True
                #Start thread
                hydroThread.start()
            print("[__main__] HydroUI active")
            """
            return None

    root = tk.Tk()
    my_gui = chromaUI(root,directories)

    root.mainloop()

    print('[__main__] Program terminated')


""" RUN MAIN FUNCTION """
print("[__main__] Starting UI...")
if __name__ == "__main__":
	runUI(file_dir)
