<h1>AutoQuant</h1>
A solution for automated gas chromatographic peak assignment and quantification
<h4>Introduction</h4>
This project aims to simplify the workflow for combining gas chromatographic (GC) data collected from multiple sources. More
specifically, it is designed to accommodate the case where GC's with flame ionization and thermal conductivity detectors are
used to collect quantitatiive data that must be labelled using data from mass spectroscopic results. This project assumes the
following setup:
<ul>
  <li>A GC equipped with FID/TCD is used to quantify gaseous products from a reaction</li>
  <li>A GC equipped with FID/MS is used to quantify liquid products from a reaction</li>
  <li>A GC equipped with FID/MS is used to label both gas and liquid reaction products</li>
</ul>
The GC's mentioned in the second and third bullets are assumed to be the same GC. This project also assumes that external software can be used to obtain spectra and integration/identification results.


<h4>The workflow</h4>
<p align="center">
  <img width="498" alt="Analytical workflow diagram demonstrating which files are necessary and which processes they are used in." src="https://github.com/JnliaH/AutoQuant/assets/173843508/c5849b00-1c46-4140-9bea-0b75af8d36af"><br>
  <b>Figure 1</b>: AutoQuant's analytical workflow
</p>

<h4>Prerequisites</h4>
As mentioned previously, this workflow assumes you have access to software that can take raw acquisition data files and produce spectra, integration values, and peak labels. Also, since there are duplicate FID signals for gas injections it is assumed you use the signal from the GC-FID/TCD. The files required to fully process analyzed samples are given in <b>Table 1</b>.<br><br>

<div align="center">
  <b>Table 1</b>: Files required for AutoQuant<br><br>
  
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
Inside of the AutoQuant documents folder are a few folders: data, resources, response-factors, and images. The data folder contains directories representing individual samples or reaction products to be analyzed. This is the most frequently used folder in AutoQuant. The resources folder contains a .csv file with known gas FID compounds used in third order assignment alongside some legacy files describing compound structure. This folder also contains the theme used in the AutoQuant UI. The response-factors folder contains several files with response factors listed by compound type and carbon number split by detector. These response factors are highly dependant on the conditions and methods used in GC analysis and therefore it is critical these are kept updated with lab-specific values for the most accurate results. Finally, the images folder contains the logo in several formats and the workflow image. <br><br>

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
│   ├── AutoQuantIcon.icns
│   ├── AutoQuantIcon.png
│   ├── AutoQuantIcon.svg
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
