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


As mentioned previously, this workflow assumes you have access to software that can take raw acquisition data files and produce spectra, integration values, and peak labels. Also, since there are duplicate FID signals for gas injections it is assumed you use the signal from the GC-FID/TCD. The files required to fully process analyzed samples are given in **Table 1**.<br><br>

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
</div>
