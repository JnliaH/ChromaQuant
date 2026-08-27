---
title: 'ChromaQuant: A Python package for chromatographic analysis and reporting'

tags:
- Python
- chromatography
- data analysis

authors:
- name: Julia N. Hancock
  orcid: 0009-0003-5786-1880
  affiliation: '1'
- name: Julie E. Rorrer
  orcid: 0000-0003-4401-8520
  affiliation: '1'

affiliations:
- index: 1
  name: University of Washington, United States of America

date: 23 August 2026

bibliography: paper.bib

---

# Summary

Analytical chromatography techniques enable the identification and quantification of species within complex chemical mixtures. These techniques, including gas chromatography (GC), high-performance liquid chromatography (HPLC), size exclusion chromatography (SEC), and ion-exchange chromatography (IEC), are applied in fields spanning the petrochemical, pharmaceutical, forensics, and food and beverage industries, to name a few. Though some samples contain only a handful of analytes, others can contain hundreds, slowing the analysis process. `ChromaQuant` was developed to fill a gap in available software for the rapid analysis of complex mixture data across multiple instruments. With extant open-source projects enabling many common chromatography operations like peak integration, `ChromaQuant` allows users to tie together multiple software programs to produce analysis deliverables like dynamic reports and matched data sets.

# Statement of need

The process of extracting useful, quantitative information from raw chromatographic data is challenging and multifaceted. An average analyst’s day-to-day needs are typically fulfilled using available commercial software such as Thermo Scientific Chromeleon [@Chromeleon], Agilent ChemStation [@ChemStation], or Shimadzu LabSolutions [@LabSolutions]. These chromatography data systems (CDSs) perform data acquisition, mass spectrum (MS) identification, signal integration, peak calibration, and reporting. However, several complicating factors render these commercial CDSs insufficient for many analysts. For one, most CDSs are typically limited to single-source data analysis and lack the capability to dynamically compare and match multiple signals. This creates a bottleneck if chromatographic data is collected across multiple instruments with different configurations (e.g., detectors, columns, methods, etc.). These CDSs are also largely designed to analyze chemical mixtures with a set number of reoccurring species, relying on static, user-specified calibration. This dependence on manual identification and assignment severely limits analysts that examine highly complex samples or samples that vary widely in composition, as identification results may depart significantly from the list of calibrated species. `ChromaQuant` is a Python package designed to facilitate routine, end-to-end chromatographic analysis and complex, source-agnostic data interpretation via several data manipulation and analysis features. The creation of `ChromaQuant` was motivated by the need to rapidly analyze petrochemical mixtures in heterogeneous catalysis research.

\newpage

# State of the field

Commercial CDSs mostly rely on user-specified calibrations for quantification and lack tools that dynamically compare results from identification with those from compound quantification. A notable exception is the Chromeleon Component Table Wizard, a tool that automatically creates a component table for multiple signals based on comparisons of collected MS or ultraviolet (UV) data to spectral libraries [@Chromeleon]. Yet, tools like these are restricted to matching peaks with comparable retention times (RTs), preventing facile comparisons of data sets collected on multiple instruments with differing configurations whose signals cannot be aligned using common techniques like retention time locking (RTL). Instead, alignment often depends on manual assessment or techniques like correlation optimized warping (COW) [@HALVORSEN2023]. As for quantification and reporting, commercial CDSs largely succeed with transparent quantification approaches and broad reporting capabilities. However, some limitations still exist: for example, quantification formulas are typically hard-coded, which can render them inflexible to users. Reports are also static and report quantitated values numerically with no facile way for users to check the veracity of applied formulas. 

There have been many efforts to develop open-source alternatives to common CDS tools. These include `hplc-py`, which offers peak deconvolution and integration [@Chure2024], `RIAssigner`, for retention index calculation [@Hecht2022], and `OpenMS`, a popular package for MS analysis with an emphasis on proteomics and metabolomics [@rost_openms_2016]. AMDIS [@AMDIS] and `matchms` [@Huber2020] also focus on comparing collected mass spectra to each other or to library reference spectra. The literature still lacks tools for rapid comparison of multiple chromatographic data sets and dynamic reporting. `ChromaQuant` fills this gap by pairing with existing tools for end-to-end chromatographic analysis.

# Software design

Chromatographic data includes, but is not limited to, chromatograms, mass spectra, component tables, and integration tables. Existing commercial software and open-source alternatives allow users to integrate raw chromatograms and produce integration tables as well as compare mass spectra against libraries to create component tables. Users then match data sets, typically by hand, and extract quantitative results using either static calibration tables or external spreadsheet software. `ChromaQuant` enables users to match comparable data sets, such as component and integration tables, using its `Table` class (\autoref{fig:hierarchy}) and `Match` module (\autoref{fig:modules}). The `Table` class functions as a wrapper around the `Pandas` [@the_pandas_development_team_2026_18675244] `DataFrame`, preserving the familiar Python interface while adding tools for data comparison and reporting. The resulting `Table` objects can be used for further analysis in Python or with another key feature of `ChromaQuant`: dynamic, Excel-based reporting that extends beyond standard Python workflows. 

Reporting in `ChromaQuant` is achieved via the `Formula` (\autoref{fig:modules}) and `Results` (\autoref{fig:hierarchy}) classes, which contain methods to create Excel formulas from user-written strings and to manage and report formulas, respectively. To create dynamic formulas, users add desired `Table` and `Value` instances to a `Results` instance before defining formulas using `Formula`. This method of formulaic reporting allows users to validate and make corrections to calculations as needed in Excel. Users can also implement conditional aggregation functions directly through use of the `Breakdown` class and its associated methods. By managing Excel calculations directly, `ChromaQuant` also enables users to leverage extant Python packages like `openpyxl` [@openpyxl] for additional automation tasks such as worksheet formatting and figure creation.

![`ChromaQuant` package hierarchy with key modules and tools highlighted.\label{fig:hierarchy}](Fig-Hierarchy_08-23-2026.png)

![Modules integrated into the Table and Results modules. The match module enables matching of multiple data sets, exemplified here by retention time matching between two signals collected on different systems. The formula module enables the creation of Excel-style formulas for dynamic reporting. The categories module enables the rapid labeling of datapoints using a user-specified category dictionary. In the top-right, “C1” and “C2” refer to different columns or instruments.\label{fig:modules}](Fig-Modules_08-23-2026.png)

\newpage

# Example usage: analysis of mixed hydrocarbons from polyethylene deconstruction

`ChromaQuant` was originally developed to facilitate the rapid analysis of complex hydrocarbon mixtures produced in the catalytic depolymerization of waste plastics such as polyethylene and polypropylene. Similar to the catalytic cracking of crude oil, the depolymerization of polyolefins can produce a complex mixture of hydrocarbons. Chromatographic analysis of these mixtures requires identifying and quantifying each product among hundreds of compounds, which often takes hours using existing software. By integrating `ChromaQuant` into this workflow, the time required to complete analysis is reduced to minutes.

Consider a case where a complex hydrocarbon mixture has been analyzed on a gas chromatograph equipped with a quantitative detector (e.g., FID) and an MS detector. These detectors produce one table with peakwise integration values and one table with identified species derived from comparing mass fragmentation patterns to a spectral library. In this example, there is also a table of empirically derived relative response factors (RFs) that relate the total amount of each product to the amount of a known mass of internal standard added to the mixture according to \autoref{eq:RF}.

\begin{equation}\label{eq:RF}
RF_i=\frac{(A_i/m_i)}{(A_s/m_s)}
\end{equation}

where i denotes a given species, s denotes the internal standard, A is the area under a peak in the quantitative (FID) chromatogram, and m denotes a mass value. To produce a quantitative report, the following analysis steps must be performed: a) the FID and MS results must be matched by retention time; b) the RFs must be matched to each species in the combined MS–FID results; and c) formulas must be applied to the resulting data set and a report generated.

![Example scheme for the GC analysis of a hydrocarbon mixture highlighting the role of existing software and the analysis gaps which `ChromaQuant` fills.\label{fig:example}](Fig-Example_08-23-2026.png)

The workflow of this example is illustrated in \autoref{fig:example}. Tabulated data are first extracted from raw chromatograms using commercial or open-source software. Then, in Python, `Table` instances are created for the MS, FID, and RF data sets. Two match operations are then performed to match the MS data to the FID data and to match the RFs to the combined MS–FID set, producing one `Table` with the results. Two `Value` instances are created for the internal standard mass and area, and these are added to a new `Results` object alongside the `Table` created in the matching steps. Finally, dynamic formulas are created using the `Formula` class; for example, the following `Formula` instantiation defines an area ratio formula:

 ```python 
area_ratio_formula = \ 
    chromaquant.formula.FORMULA_IF_ERROR( 
        chromaquant.formula.FORMULA_DIVISION( 
            some_table.insert('Area'), 
            internal_standard_area.insert() 
        ) 
    ) 
``` 

Here, a new `Formula` is created using two base formula templates: FORMULA_IF_ERROR and FORMULA_DIVISION. The inner formula calculates the ratio of a species’ area to the internal standard area using the `insert` attribute of `Value` and `Table`. The outer formula wraps this ratio in the Excel formula IF_ERROR to default erroneous calculations to zero. Additional `Formulas` can then be created to extract the internal standard area from the results table and to calculate the mass of each species (by solving for $m_i$ in \autoref{eq:RF}). Once all `Formulas` and `DataSets` have been added, the results are exported directly to Excel using the `report_results` method of the `Results` class. 

# Research impact statement

`ChromaQuant` is actively being used in the Rorrer Lab at the University of Washington to automate the chromatographic analysis of products from the heterogeneous catalytic deconstruction of plastic waste. The package is being used in projects involving the hydrogen-free deconstruction of polyolefins and base-catalyzed depolymerization of polystyrene, and is also being integrated into an autonomous platform for self-optimizing flow reactors. Project development has taken an iterative approach, from the self-standing application demonstrated in 2024 [@Hancock2024] to the current Python package with automated testing and continuous integration workflows. `ChromaQuant` is designed to facilitate automated analyses for a broad range of 1D chromatographic applications, regardless of instrument specifications. To facilitate community engagement, the repository hosts a reproducible example of package utilization, extensive documentation, and an open issues board. 

# AI usage disclosure

No generative AI tools were used in the development of this package or in the preparation of this manuscript or its supporting materials.

# Acknowledgements

This material was supported by the ACS Petroleum Research Fund under Grant No. 68444-DNI5 and the National Science Foundation Graduate Research Fellowship under Grant No. DGE-2140004. We thank Professor David Beck for his technical advice on the manuscript. 

\newpage

# References