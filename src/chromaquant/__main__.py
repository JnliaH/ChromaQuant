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
version = "0.3.1"
__version__ = version

""" DIRECTORIES """
print("[__main__] Defining directories...")
print("[__main__] Using Handle package...")
#Get directories from handling script
directories = hd.handle(os.path.dirname(os.path.abspath(__file__)))

""" DATA SEARCH """
print("[__main__] Searching for valid data files...")
#Get a list of all available sample data directories (excluding "old") in the data files directory
sampleList = [f.name for f in os.scandir(directories['data']) if f.is_dir() if f.name != "old"]

""" CODE """
#Define ChromaQuantUI as class
class chromaUI:

    runFIDpMS_function = lambda x: x+1

    #Initialization function – master here will be our root widget
    def __init__(self, master, directories):

        self.master = master
        self.directories = directories
        #Standard padding
        self.std_padx = 10
        self.std_pady = 10

        #Padding for widgets/widget rows
        self.widget_padx = 20
        self.widget_pady = 10

        #Initialize user variable dictionary
        self.var_dict = {}
        self.setupUI()

        #Create font objects
        self.title_font = tkFont.Font(size=18,weight='bold')   #Title font
        
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

        #UNKNOWNS ANALYSIS POSTPROCESS
        #Add a frame for the UA_UPP script
        self.uppFrame = ttk.LabelFrame(self.rowoneFrame,text='Unknowns Analysis Postprocessing',style='QuantLabelframe.TLabelframe')
        self.uppFrame.grid(column=1,row=0,sticky='NSWE',padx=self.widget_padx,pady=self.widget_pady)
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
        self.quantFrame.grid(column=1,row=0,sticky='NSWE',padx=self.widget_padx,pady=self.widget_pady)
        self.setupQuant()

        #HYDROUI
        #Add a frame for the hydroUI script
        self.hydroFrame = ttk.LabelFrame(self.rowtwoFrame,text='HydroUI',style='QuantLabelframe.TLabelframe')
        self.hydroFrame.grid(column=3,row=0,sticky='NSWE',padx=(0,self.widget_padx),pady=self.widget_pady)
        self.setupHydro()

    def greet(self):
        print("Greetings!")
    
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
    
        root.geometry("880x1000")
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
    
    def setupUPP(self):

        #Add start button
        self.setupStartButton(self.uppFrame,[0,0],[20,20],1,self.runUPP)

    def setupMatch(self):
    
        #Add text to the top of the frame
        tk.Label(self.matchFrame,text='Please enter all information')\
            .grid(column=0,row=0,columnspan=4,padx=self.std_padx,pady=self.std_pady)
        
        #Add a radiobutton set for selecting sample type
        self.setupRadioButton(self.matchFrame,'Please select the sample type:',[0,1],[20,20],1,'fpm_typevar',{'Liquid':'L','Gas':'G'},self.greet,'L')
        #Add a radiobutton set for selecting match model
        self.setupRadioButton(self.matchFrame,'Please select the desired matching fit model:',[0,2],[20,20],1,'fpm_modelvar',{'Retention\nTime':'R','Third\nOrder':'T','Linear':'L'},self.greet,'R')
        #Add start button
        self.setupStartButton(self.matchFrame,[0,3],[20,20],4,self.runMatch)

    def setupQuant(self):

        #Add text to the top of the frame
        tk.Label(self.quantFrame,text='Please enter all information')\
            .grid(column=0,row=0,columnspan=4,padx=self.std_padx,pady=self.std_pady)
        
        #Add a radiobutton set for selecting sample type
        self.setupRadioButton(self.quantFrame,'Which components are present in the sample?',[0,1],[20,20],1,'quant_typevar',{'Liquid\nOnly':'L','Gas\nOnly':'G','Liquid\nand Gas':'LG'},self.greet,'L')
        
        #Add start button
        self.setupStartButton(self.quantFrame,[0,2],[20,20],4,self.runQuant)

    def setupHydro(self):

        #Add start button
        self.setupStartButton(self.hydroFrame,[0,0],[20,20],1,self.runHydro)

    def setupStartButton(self,frame,placement,pad,columnspan,function):

        #Add a start button
        fidpms_sbutton = ttk.Button(frame,text="\n\n\nRun Script\n\n\n",width=20,style='Accent.TButton',command=function)
        fidpms_sbutton.grid(column=placement[0],row=placement[1],padx=pad[0],pady=pad[1],columnspan=columnspan)

    def setupRadioButton(self,frame,label_text,placement,pad,columnspan,var_name,option_val_dict,function,init_state='Option Blank'):
        
        #placement = [column,row]
        #pad = [padx,pady]
        #var_dict = {'var_1':tk.StringVar(),...}
        #var_name = 'var_1'
        #text_val_dict = {'option_1':'value_1',...}

        #Set up a radiobutton for selecting liquid or gas
        #Add a label
        tk.Label(frame,text=label_text).grid(column=placement[0],row=placement[1],padx=pad[0],pady=pad[1],columnspan=columnspan,sticky='e')
        #Define var_name entry in class's var_dict
        self.var_dict[var_name] = tk.StringVar()
        
        #Define current column as column to the right of label
        current_col = placement[0] + 1
        #Define radiobutton padding loop iterable
        current_pad = 0
        #Define list to iterate through for radiobutton padding
        radiopad = [(10,10) for i in range(len(option_val_dict))]
        radiopad[-1] = (10,20)

        #For every option in the option-value dictionary, add a radiobutton (iterate over columns)
        for option in option_val_dict:

            #Add the radiobutton
            ttk.Radiobutton(frame , text=option , variable=self.var_dict[var_name] , value=option_val_dict[option] , command=function)\
                .grid(column=current_col , row=placement[1] , padx=radiopad[current_pad] , sticky='w')
            
            #Iterate current column and radio padding list
            current_col += 1
            current_pad += 1

        #Select the initial radiobutton state based on the init_state argument
        #If init_state is 'Option Blank', select the first radiobutton
        if init_state == 'Option Blank':
            self.var_dict[var_name].set(next(iter(option_val_dict.values())))

        #Otherwise, if the init_state does not have a counterpart in the values of the option_val_dict, select the first radiobutton
        elif init_state not in option_val_dict.values():
            self.var_dict[var_name].set(next(iter(option_val_dict.values())))
        
        #Otherwise, select the specified radiobutton
        else:
            self.var_dict[var_name].set(init_state)

    def sampleSelect(self,event):
        sname = self.sampleBox.get()
        print("User selected " + self.sampleBox.get())
        return sname

    def runUPP(self):
        #Function for running the UPP function
        print("[__main__] Running Unknowns Postprocessing...")
        return None
    
    def runMatch(self):
        #Function for running the match function
        print("[__main__] Running FID and MS matching...")
        mt.mainMatch(self.var_dict['sampleVar'].get(),self.var_dict['fpm_typevar'].get())
        return None
    
    def runQuant(self):
        #Function for running the quantification function
        print("[__main__] Running quantification...")
        #qt.mainQuant()
        return None
    
    def runHydro(self):

        print("[__main__] Running HydroUI...")
        return None
    
root = tk.Tk()
my_gui = chromaUI(root,directories)

root.mainloop()


