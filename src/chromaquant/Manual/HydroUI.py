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

SCRIPT WHICH RUNS A DESKTOP APPLICATION FOR FUTURE USE IN SPECTRA VISUALIZATION

Julia Hancock
Started 11/21/2023

"""

""" PACKAGES """
import sys
import pandas as pd
#Dash and plotly – dcc = "Dash Core Components", px = "Plotly express" with visualization tools
from dash import Dash, html, dash_table, dcc, callback, Output, Input
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.graph_objects as go
from pubchempy import Compound, get_compounds
from rdkit import Chem
from rdkit.Chem.Draw import MolsToGridImage, MolDrawing, rdMolDraw2D
import base64
from io import BytesIO
import os
from molmass import Formula

""" PARAMETERS """
#Write sample name
sname = "MBPR048_01"

#Write whether sample is liquid ("L") or gas ("G")
stype = "G"

#Write whether there exists a file containing matched FID and MS peaks (True/False)
smatchtf = False

""" DIRECTORIES """
#Current script directory
script_directory = os.path.dirname(__file__)

""" DATA IMPORTS """
#Define file names using user parameters
if stype == "G":
    fn_FID_SPEC = sname+"_GS2_FID_SPEC.csv"
    fn_MS_SPEC = sname+"_GS1_MS_SPEC.csv"
    
    if smatchtf == True:
        fn_FPM = sname+"_GS2_FIDpMS.csv"
    else:
        fn_FPM = "default_FIDpMS.csv"

if stype == "L":
    fn_FID_SPEC = sname+"_LQ1_FID_SPEC.csv"
    fn_MS_SPEC = sname+"_LQ1_MS_SPEC.csv"
    
    if smatchtf == True:
        fn_FPM = sname+"_LQ1_FIDpMS.csv"
    else:
        fn_FPM = "default_FIDpMS.csv"

#Define directories for desired dataframes
DIR_LQ_FIDpMS_PeaksLB = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/Quantification/data/"+sname+"/"+fn_FPM
DIR_LQ_FID_SPEC = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/Quantification/data/"+sname+"/"+fn_FID_SPEC
DIR_LQ_MS_SPEC = "/Users/connards/Desktop/University/Rorrer Lab/Scripts/Quantification/data/"+sname+"/"+fn_MS_SPEC
#Column names to add to imported spectral data
col_names_SPEC = ['RT','Signal']

#Read matched peak data between FID and MS
LQ_FIDpMS_PeaksLB = pd.read_csv(DIR_LQ_FIDpMS_PeaksLB)

#Read spectra data for FID
LQ_FID_SPEC = pd.read_csv(DIR_LQ_FID_SPEC, names=col_names_SPEC, header=None)
#Add column labeling FID data
LQ_FID_SPEC['SignalType'] = 'FID'

#Read spectra data for MS
LQ_MS_SPEC = pd.read_csv(DIR_LQ_MS_SPEC, names=col_names_SPEC, header=None)
#Add column labeling MS data
LQ_MS_SPEC['SignalType'] = 'MS'

#Get dictionary of checklist entries to SignalType entries
dictSPEC = {'FID':'FID','MS':'MS'}
#Get list of checklist keys
dictSPEC_keys = list(dictSPEC.keys())

#Append MS dataframe to FID dataframe
LQ_FIDpMS_SPEC = pd.concat([LQ_FID_SPEC,LQ_MS_SPEC],ignore_index=True)

""" ACCESSING PUBCHEM """

#If there exists FIDpMS files, proceed
if smatchtf == True:
    #Create a copy of the PeaksLB dataframe called PeaksLB_SMILES
    PeaksLB_Smiles = LQ_FIDpMS_PeaksLB.copy()
    #Read the existing smilePairs.csv
    smilePairs = pd.read_csv(os.path.join(script_directory,'resources','smilePairs.csv'))
    #Add a column to the PeaksLB dataframe with the smiles of matched compounds, ignoring 'No match'
    PeaksLB_Smiles['isoSMILES'] = ''
    #List of indices with compound names
    compindex = []
    #Set up temporary smile string for use in for loop
    tempSmile = smilePairs.loc[smilePairs['Compound Name']==PeaksLB_Smiles.at[4,'Compound Name']]

    #Loop through all rows in PeaksLB_Smiles
    print('[MAIN] Assessing compound structures through SMILES...')
    for i, row in PeaksLB_Smiles.iterrows():
        
        #Only add peaks with matched compounds
        if PeaksLB_Smiles.at[i,'Compound Name'] != 'No match' and PeaksLB_Smiles.at[i,'Compound Name'] != 'No Match':
            
            #Try/except to catch error in accessing dataframe
            try:
                #If the compound name can be found in the compound-SMILES .csv file, add to dataframe
                if any(smilePairs['Compound Name']==row['Compound Name']):
                    tempSmile = smilePairs.loc[smilePairs['Compound Name']==row['Compound Name'],'isoSMILES']
                    #Choose the first SMILES in the series
                    tempSmile = tempSmile[tempSmile.index[0]]
                    #Save SMILES to PeaksLB_Smiles dataframe
                    PeaksLB_Smiles.at[i,'isoSMILES'] = tempSmile
                #If the compound isn't in the list, get SMILES from PubCHEM
                else:
                    PeaksLB_Smiles.at[i,'isoSMILES'] = get_compounds(PeaksLB_Smiles.at[i,'Compound Name'],\
                                                                     'name')[0].isomeric_smiles
                    print('[MAIN] Downloading SMILES for {0}...'.format(PeaksLB_Smiles.at[i,'Compound Name']))
                    compindex.append(i)
                    
            except:
                print('[ERROR] An error occurred in accessing SMILES for {0}'.format(row['Compound Name']))

        else:
            pass

    #If any compounds were previously unlabelled, save the compound name and SMILES pairs as a .csv
    smilePairsOut = pd.concat([smilePairs,PeaksLB_Smiles.loc[compindex,['Compound Name','isoSMILES']]],ignore_index=True)
    if smilePairsOut.size > smilePairs.size:
        print("[MAIN] Saving updated compound-SMILES pairs...")
        smilePairsOut.to_csv(os.path.join(script_directory,'resources','smilePairs.csv'),index=False)
    else:
        pass


    """ LABELLING SPECTRA """
    print("[MAIN] Labelling the FID spectrum using the peak-compound dataframe...")
    #Find only the PeaksLB_Smiles rows which have compound matches
    PeaksLB_Smiles = PeaksLB_Smiles[~PeaksLB_Smiles['Compound Name'].isin(['No Match','No match'])]
    #For every entry in this new PeaksLB_Smiles dataframe, find the nearest FID Spectra RT to the labelled peak RT's
    for i, row in PeaksLB_Smiles.iterrows():
        #Find the closest row index in LQ_FID_SPEC
        df_closestIN = LQ_FID_SPEC.iloc[(LQ_FID_SPEC['RT']-row['FID RT']).abs().argsort()[:1]].index[0]
        #Add four columns to the spectral data: compound name, formula, match factor, and isosmiles
        LQ_FID_SPEC.at[df_closestIN,'Compound Name'] = row['Compound Name']
        LQ_FID_SPEC.at[df_closestIN,'Formula'] = row['Formula']
        LQ_FID_SPEC.at[df_closestIN,'Match Factor'] = row['Match Factor']
        LQ_FID_SPEC.at[df_closestIN,'isoSMILES'] = row['isoSMILES']
        #Find the molecular weight of the given compound and assign to a new column in the spectral data
        LQ_FID_SPEC.at[df_closestIN,'MW'] = Formula(row['Formula']).mass

#Otherwise, pass
else:
    pass

""" WEB APPLICATION """

#Initialize the application with the Dash constructor
app = Dash(__name__)

#App layout
app.layout = html.Div([
    
    #First row
    html.Div(children=[
        #First row first column
        html.Div(children=[
        #Scatter plot inside of a dcc interactive figure module
        dcc.Graph(id='controls_and_graph')],\
                  style={'display':'inline-block','vertical-align':'top','margin-left': 5,'margin-top': '3vw','width':'70%'}),
        
        #First row second column
        html.Div(children=[
            #Checklist for selecting viewed data
            html.Div(children=[dcc.Checklist(dictSPEC_keys,[dictSPEC_keys[0]],id='controls_and_checklist')],style={'margin-top':100},className='row'),
            #Axis limit entries
            #x limit lower
            html.Div(children=[dcc.Input(id='xlim_l',type='number',placeholder='Lower x-limit')],style={'margin-top':20},className='row'),
            #x limit upper
            html.Div(children=[dcc.Input(id='xlim_u',type='number',placeholder='Upper x-limit')],className='row'),
            #y limit lower
            html.Div(children=[dcc.Input(id='ylim_l',type='number',placeholder='Lower y-limit')],className='row'),
            #y limit upper
            html.Div(children=[dcc.Input(id='ylim_u',type='number',placeholder='Upper y-limit')],className='row'),
            #y2 limit lower
            html.Div(children=[dcc.Input(id='y2lim_l',type='number',placeholder='Secondary Lower y-limit')],className='row'),
            #y2 limit upper
            html.Div(children=[dcc.Input(id='y2lim_u',type='number',placeholder='Secondary Upper y-limit')],className='row')],
        
        #Set display style to inline-block
        style={'display':'inline-block','vertical-align':'middle','margin-left': 0,'margin-top': '3vw','width':'25%'})],
        className='row'),
    
    #Second row
    html.Div(children=[
        #Compound structure image
        html.Img(id='structure-image')],className='row')
    
    ])

""" CALLBACK CONTROLS """
#FID and MS spectra selection and axis limits callback
@callback(
    Output(component_id='controls_and_graph',component_property='figure'),
    Input(component_id='controls_and_checklist',component_property='value'),
    Input('xlim_l','value'),
    Input('xlim_u','value'),
    Input('ylim_l','value'),
    Input('ylim_u','value'),
    Input('y2lim_l','value'),
    Input('y2lim_u','value')
)
#Callback graph updating function
def update_graph(fig_chosen,xlim_lval,xlim_uval,ylim_lval,ylim_uval,y2lim_lval,y2lim_uval):
    #Format axis limits into a list
    axLim = [xlim_lval,xlim_uval,ylim_lval,ylim_uval,y2lim_lval,y2lim_uval]
    #Dictionary of colors for specific use for MS and FID spectra
    colorDict = {'FID':px.colors.qualitative.Safe[4],'MS':px.colors.qualitative.Safe[1]}
    #List of applicable dataframe titles based on fig_chosen as keys in dictSPEC
    fig_chosen_dictSPEC = [dictSPEC[i] for i in fig_chosen]
    #Filter DataFrame based on fig_chosen
    #filDF = LQ_FIDpMS_SPEC[LQ_FIDpMS_SPEC['SignalType'].isin(fig_chosen_dictSPEC)]
    
    #Initialize figure
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    #If there are any spectra chosen, plot them
    if len(fig_chosen) != 0:
        #Add a trace to the figure for each entry in fig_chosen
        for i in range(len(fig_chosen_dictSPEC)):
            #If the entry is past the first, set secondary_y axis value to True, otherwise set to False
            if i > 0:
                yTF = True
            else:
                yTF = False
            #Filter DataFrame based on ith entry in fig_chosen_dictSPEC
            filDF = LQ_FIDpMS_SPEC[LQ_FIDpMS_SPEC['SignalType'].str.match(fig_chosen_dictSPEC[i])]
            
            #Add a trace
            fig.add_trace(go.Scattergl(x=filDF['RT'],y=filDF['Signal'],\
                                     name=fig_chosen_dictSPEC[i],marker=dict(color=colorDict[fig_chosen[i]]),mode='lines+markers'),\
                                     secondary_y=yTF)
        
        #Update figure layout by adding titles
        fig.update_layout(title={'text':sname+' Spectra','font':{'color':'rgb(76, 46, 132)','size':20,'family':'Arial'}},\
                                  legend_title='Displayed Spectra')
        fig.update_xaxes(title_text='Retention time (min)')
        fig.update_yaxes(title_text=fig_chosen_dictSPEC[0]+' Signal (a.u.)',secondary_y=False)
        #Add a secondary y-axis title if necessary
        if len(fig_chosen_dictSPEC) > 1:
            fig.update_yaxes(title_text=fig_chosen_dictSPEC[1]+' Signal (a.u.)',secondary_y=True)
            #Check if user-inputted axis limits are viable
            #If lower ylim is less than upper ylim, update y-axis
            #If any NoneType exist in the axis limits list, do not update limits
            if None not in axLim[4:] and axLim[4] < axLim[5]:
                fig.update_yaxes(range=[axLim[4],axLim[5]],secondary_y=True)
            else:
                pass
        else:
            pass
    
        #Check if user-inputted axis limits are viable
        #If lower xlim is less than upper xlim, update x-axis
        #If any NoneType exist in the axis limits list, do not update limits
        if None not in axLim[:1] and axLim[0] < axLim[1]:
            fig.update_xaxes(range=[axLim[0],axLim[1]])
        else:
            pass
        #If lower ylim is less than upper ylim, update y-axis
        #If any NoneType exist in the axis limits list, do not update limits
        if None not in axLim[2:4] and axLim[2] < axLim[3]:
            fig.update_yaxes(range=[axLim[2],axLim[3]],secondary_y=False)
        else:
            pass
        
    #If no spectra are chosen, don't plot anything
    else:
        pass
    
    return fig


#Compound structure drawing function
@callback(
    Output('structure-image','src'),
    Input('controls_and_graph','selectedData')
)
def draw_structure(selectedData):
    max_structs = 6
    empty_plot = "data:image/gif;base64,R0lGODlhAQABAAAAACwAAAAAAQABAAA="
    
    if selectedData:
        #Take first point in selectedData, creating nested list
        checkPoint = [selectedData['points'][0]['curveNumber'],\
                       selectedData['points'][0]['x'],\
                       selectedData['points'][0]['y']]

        #Dictionary assigning each spectra to a curve number
        specKeys = {'FID':'','MS':''}
        
        #Assign spectra to curve numbers according to whether or not the first point matches any points in the FID signal
        try:
            if checkPoint[2] == LQ_FID_SPEC.at[LQ_FID_SPEC[LQ_FID_SPEC['RT']==checkPoint[1]].index[0],'Signal']:
                specKeys['FID'] = int(checkPoint[0])
                specKeys['MS'] = int(not checkPoint[0])
            else:
                pass
        except:
            specKeys['FID'] = int(not checkPoint[0])
            specKeys['MS'] = int(checkPoint[0])
        
        #Create list of selected points filtered so only FID results show
        selectedFIDData = []
        for i in selectedData['points']:
            if i['curveNumber'] == specKeys['FID']:
                selectedFIDData.append({'x':i['x'],'y':i['y'],'pointIndex':i['pointIndex']})
        
        if len(selectedFIDData) == 0:
            return empty_plot
        #List of selected point indices on FID spectrum
        match_idx = [x['pointIndex'] for x in selectedFIDData]
        #Dataframe with smiles and related data for selected points
        smilesDF = LQ_FID_SPEC.loc[match_idx,['RT','Compound Name','Formula','Match Factor','isoSMILES']]
        #Set FID spectra index to its own column and reset the indices
        smilesDF.reset_index(inplace=True)
        smilesDF = smilesDF.rename(columns={'index':'Spectra Index'})
        #Filter dataframe to only include non-NaN smiles entries
        smilesDF_F = smilesDF[smilesDF['isoSMILES'].notnull()].reset_index(drop=True)
        #Get lists of smiles rdkit objects and corresponding compound names
        list_smiles = [Chem.MolFromSmiles(x) for x in smilesDF_F['isoSMILES'].tolist()][:max_structs]
        #Create a list of legend entries using data from smilesDF_F
        list_legends = [smilesDF_F.loc[smilesDF_F.index[i],'Compound Name']+'\n'+\
                        smilesDF_F.loc[smilesDF_F.index[i],'Formula']+' - '+\
                        '{:.4}% Match'.format(smilesDF_F.loc[smilesDF_F.index[i],'Match Factor'])+'\n'+\
                        '{:.3} min'.format(smilesDF_F.loc[smilesDF_F.index[i],'RT']) for i in range(len(smilesDF_F))][:max_structs]
        #Initialize MolDraw2DCairo drawer
        drawer = rdMolDraw2D.MolDraw2DCairo(1200,180,200,180)
        #Set drawing options
        drawer.drawOptions().useBWAtomPalette()
        drawer.drawOptions().legendFontSize = 16
        drawer.drawOptions().legendFraction = 0.3
        drawer.drawOptions().maxFontSize = 16
        drawer.drawOptions().padding = 0.05
        drawer.drawOptions().centreMoleculesBeforeDrawing = True
        #Draw the molecules
        drawer.DrawMolecules(list_smiles,legends=list_legends)
        drawer.FinishDrawing()
        #Set buffered image using BytesIO encoding
        buffered = BytesIO(drawer.GetDrawingText())
        
        #OLD METHOD FOR DRAWING GRID OF MOLECULE IMAGES
        #Create a grid of molecule images using rdkit
        #img = MolsToGridImage(list_smiles[0:max_structs], molsPerRow=structs_per_row, legends=list_legends, subImgSize=(300,300))
        #img = SVG(drawer.GetDrawingText())
        #Encode and save the image
        #buffered = BytesIO()
        #img.save(buffered, format="JPEG")
        
        #Encode the image
        encoded_image = base64.b64encode(buffered.getvalue())
        #Define and return the image string
        src_str = 'data:image/png;base64,{}'.format(encoded_image.decode())
        return src_str
    else:
        #Return a blank string
        return ''

""" EXECUTE APPLICATION """

#Run the application
if __name__ == '__main__':
    app.run(debug=True)

    
"""
#Callback controls
@callback(
    Output(component_id='controls_and_graph',component_property='figure'),
    Input(component_id='controls_and_checklist',component_property='value')   
)

def update_graph(fig_chosen):
    #List of applicable dataframe titles based on fig_chosen as keys in dictSPEC
    fig_chosen_dictSPEC = [dictSPEC[i] for i in fig_chosen]
    #Filter DataFrame based on fig_chosen
    filDF = LQ_FIDpMS_SPEC[LQ_FIDpMS_SPEC['SignalType'].isin(fig_chosen_dictSPEC)]
    fig = px.scatter(filDF,x='RT',y='Signal',color='SignalType',\
                     color_discrete_sequence=[px.colors.qualitative.Safe[4],\
                                              px.colors.qualitative.Safe[1]])
    #Update figure layout
    fig.update_layout(title='MBPR031 Spectra',xaxis_title='Retention time (min)',yaxis_title='Signal (a.u.)',legend_title='Displayed Spectra')
    return fig
"""
    
    
    
    
    
    
    
