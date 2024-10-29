<h1>ChromaQuant</h1>
<i>A solution for automated gas chromatographic peak assignment and quantification</i>

<h4>Introduction</h4>
<img style="float: right;" align="right" width="256" alt="ChromaQuant Logo" src="https://github.com/JnliaH/ChromaQuant/blob/rebrand/images/ChromaQuantIcon.png">
This project aims to simplify the workflow for combining gas chromatography (GC) data collected from multiple sources. More
specifically, it is designed to accommodate the case where GCs with flame ionization and thermal conductivity detectors are
used to collect quantitative data that must be labelled using data from mass spectroscopic results. This project assumes the
following setup:
<ul>
  <li>A GC equipped with FID/TCD is used to quantify gaseous products from a reaction</li>
  <li>A GC equipped with FID/MS is used to quantify liquid products from a reaction</li>
  <li>A GC equipped with FID/MS is used to label both gas and liquid reaction products</li>
</ul>
The GCs mentioned in the second and third bullets are assumed to be the same GC. This project also assumes that external software can be used to obtain spectra and integration/identification results.<br><br>

Relative response factors (or simply "response factors" or RFs from now on) are used to get quantitative data from liquid FID results. These are defined as:

$$RF = \frac{(A_i/A_s)}{m_i/m_s}$$

Where $A_i$ is the Area for the species of interest, $A_s$ is the area of the internal standard, $m_i$ is the mass of the species of interest, and $m_s$ is the mass of the internal standard. In the Rorrer Lab, we use 1,3,5-tri-tert-butylbenzene as an internal standard. Response factors are determined by making solutions (~6) of known concentration across a given concentration range and applying a linear fit. Interpolation/extrapolation is used for cases where response factors are not known using fits determined in the liquid FID RFs Excel sheet. Gas TCD integration values are quantified by using (non-relative) response factors defined as:

$$RF = \frac{Area}{Volume Percent}$$

Quantitative data is then determined by getting a total volume of gas collected by dividing the amount of CO2 (the internal standard) injected by the vol.% CO2. This total volume is then used alongside volume percents for each species of interest and the ideal gas law to determine the quantity of each product. Again, RFs are determined using external calibration gas injections. Gas FID integration is quantified similarly, except the total volume of gas determined in the TCD step is used since CO2 does not show up separately in the FID chromatogram.

<h4>Installation</h4>
To install on a MacOSX system, simply download the dist directory from the remote repository alongside the resources, response-factors, and images folders. Copy the ChromaQuant directory from the dist directory and paste it in the desired location. Locate the "ChromaQuant/_internal/properties.json" file in this pasted directory and edit the "app-directory" value to read the absolute path to the ChromaQuant UNIX executable and the "file-directory" value to read the desired path to ChromaQuant data files. Finally, create a folder named ChromaQuant at the location of the file-directory path.<br><br>

It is recommended that the ChromaQuant folder be placed in the Applications folder and the file directory (a.k.a. the ChromaQuant documents folder) to be created in the "Users/[User]/Documents" folder. 

Create an empty folder inside the documents folder named data. Paste the resources, response-factors, and images folder into the documents folder. Note that the resources and response-factors folder contain data relevant to the Rorrer Lab – response factors and known compounds depend highly on reactions and reaction conditions studied, GC acquisition methods, and column configuration.

Finally, test that the ChromaQuant executable runs by navigating to the app directory and double clicking the executable. If it does, you can (optionally) set the executable's icon to the ChromaQuantIcon.icns found in the images directory and make aliases as desired.

<h4>The workflow</h4>
<p align="center">
  <img width="498" alt="Analytical workflow diagram demonstrating which files are necessary and which processes they are used in." src="https://github.com/JnliaH/ChromaQuant/assets/173843508/c5849b00-1c46-4140-9bea-0b75af8d36af"><br>
  <b>Figure 1</b>: ChromaQuant's analytical workflow
</p>

<h4>Prerequisites</h4>
As mentioned previously, this workflow assumes you have access to software that can take raw acquisition data files and produce spectra, integration values, and peak labels. Also, since there are duplicate FID signals for gas injections it is assumed you use the signal from the GC-FID/TCD. The files required to fully process analyzed samples are given in <b>Table 1</b>.<br><br>

<div align="center">
  <b>Table 1</b>: Files required for ChromaQuant<br><br>
  
  |           File Name             |                             Description                               |
  | :-----------------------------: | :-------------------------------------------------------------------: |
  |[Sample]_[Injection]_LQ1_FID_SPEC| Sample's FID spectra acquired from liquid sample injection            |
  |[Sample]_[Injection]_LQ1_MS_SPEC | Sample's MS spectra acquired from liquid sample injection             |
  |[Sample]_[Injection]_LQ1_FID_CSO | Sample's FID integration values acquired from liquid sample injection |
  |[Sample]_[Injection]_LQ1_UA_UPP  | Sample's FID spectra acquired from liquid sample injection            |
  |[Sample]_[Injection]_GS1_MS_SPEC | Sample's MS spectra acquired from gas sample injection                |
  |[Sample]_[Injection]_GS2_FID_SPEC| Sample's FID spectra acquired from gas sample injection               |
  |[Sample]_[Injection]_GS2_TCD_SPEC| Sample's TCD spectra acquired from gas sample injection               |
  |[Sample]_[Injection]_GS2_TCD_CSO | Sample's FID spectra acquired from liquid sample injection            |
  |[Sample]_[Injection]_GS1_UA_UPP  | Sample's FID spectra acquired from liquid sample injection            |
  |[Sample]_INFO.json               | JSON containing necessary information about the sample                |
</div>

The FID, MS, and TCD spectra must all be .csv files with no headers and two columns. The first column (again, unlabeled) must represent retention times (in minutes) and the second column must represent the signal at each row's retention time. 

The UA_UPP files must be .csv files that contain the columns "Component RT", "Compound Name", "Formula", and "Match Factor", in no particular order. These files should contain a list of all compounds identified in the MS spectra alongside their MS retention time (min), formula (standard molecular formula format, numbers not expressed as subscripts), and the match factor assigned by the MS interpretation software library search (0-100).

The CSO files must be .csv files that contain the columns "Signal Name", "RT", "Area", and "Height", in no particular order. The LQ1_FID_CSO file should contain a list of all integrated peaks in the FID spectra from liquids analysis, including these peaks retention times, area, and height. The GS2_TCD_CSO file should contain a list of all integrated peaks in the FID and TCD spectra from gas analysis. In the case of LQ1, the signal name should be FID1A for every peak; for GS2, the signal name should be FID1A for the FID peaks and TCD2B for the TCD peaks. This program uses the signal name to distinguish between FID and TCD results for the gas phase analysis – there aren't separate files for these two lists of integration values.

The INFO file must be a .json file containing the following information in the following format. A file version of this .json data is found under the root directory as "empty_INFO.json".

```json
{
    "Sample Name":                 "[Sample]_[Injection]",
    "Reactor Name":                "[Reactor name]",
    "Catalyst Type":               "[Catalyst name, be as descriptive as possible]",
    "Catalyst Amount (mg)":        "[Catalyst added to reactor, sum masses if more than one catalyst]",
    "Plastic Type":                "[Name of substrate added, be as descriptive as possible]",
    "Plastic Amount (mg)":         "[Mass of substrate added]",
    "Reaction Temperature (C)":    "[Temperature of reactor before quenching]",
    "Quench Temperature (C)":      "[Temperature of reactor after quenching]",
    "Reaction Pressure (psi)":     "[Pressure of reactor before quenching]",
    "Initial Pressure (psi)":      "[Initial charge pressure of reactor]",
    "Quench Pressure (psi)":       "[Pressure of reactor after quenching",
    "Start Time":                  "[Start time in format yyyy-mm-dd hh:mm:ss.000]",
    "End Time":                    "[End time in format yyyy-mm-dd hh:mm:ss.000]",
    "Heat Time":                   "[Time taken to reach reaction temperature from room temperature]",
    "Internal Standard Name":      "[Name of external/internal standard]",
    "Internal Standard Mass (mg)": "[Mass of external/internal standard]",
    "Reactor Volume (mL)":         "[Reactor total volume]",
    "Remaining solids (mg)":       "[Weight of dry residual solids]",
    "Injected CO2 (mL)":           "[Volume of CO2 injected into gas bag containing gas sample]"
}
```

<h4>Data Structure</h4>
Inside of the ChromaQuant documents folder are a few folders: data, resources, response-factors, and images. The data folder contains directories representing individual samples or reaction products to be analyzed. This is the most frequently used folder in ChromaQuant The resources folder contains a .csv file with known gas FID compounds used in third order assignment alongside some legacy files describing compound structure. This folder also contains the theme used in the ChromaQuant UI. The response-factors folder contains several files with response factors listed by compound type and carbon number split by detector. These response factors are highly dependant on the conditions and methods used in GC analysis and therefore it is critical these are kept updated with lab-specific values for the most accurate results. Finally, the images folder contains the logo in several formats and the workflow image. <br><br>

```bash
.
├── data
│   └── example2
│       ├── breakdowns
│       │   ├── example2_Breakdown_20240729 (1).xlsx
│       │   └── example2_Breakdown_20240729.xlsx
│       ├── example2_INFO.json
│       ├── log
│       │   └── quantlog_20240729.log
│       ├── manual
│       │   └── MBPR053_02_ManualBreakdown.xlsx
│       └── raw data
│           ├── example2_GS1_MS_SPEC.csv
│           ├── example2_GS1_UA_Comp_UPP.csv
│           ├── example2_GS2_FID_SPEC.CSV
│           ├── example2_GS2_FIDpMS.csv
│           ├── example2_GS2_TCD_CSO.csv
│           ├── example2_GS2_TCD_SPEC.CSV
│           ├── example2_LQ1_FID_CSO.csv
│           ├── example2_LQ1_FID_SPEC.CSV
│           ├── example2_LQ1_FIDpMS.csv
│           ├── example2_LQ1_MS_SPEC.csv
│           └── example2_LQ1_UA_Comp_UPP.csv
├── images
│   ├── ChromaQuantIcon.icns
│   ├── ChromaQuantIcon.png
│   ├── ChromaQuantIcon.svg
│   └── workflow.png
├── resources
│   ├── KnownCompoundsAuto.xlsx
│   ├── gasPairs_FIDpMS.csv
│   ├── known_compounds.csv
│   └── smilePairs.csv
└── response-factors
    ├── FIDRF_7-24-24.csv
    ├── LRF_7-24-24.xlsx
    ├── TCDRF_7-24-24.csv
    └── liquidRFFits.csv
```

For a given sample, all data files listed in **Table 1** should be placed in the "data/[Sample]/raw data" directory except for the INFO.json, which should be placed in the "data/[Sample]" directory.
