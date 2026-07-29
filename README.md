<h1>ChromaQuant</h1>

[![Static Badge](https://img.shields.io/badge/Rorrer-Lab-Blue?labelColor=32006e&color=85754d&link=https%3A%2F%2Fwww.rorrerlab.com%2F)](https://www.rorrerlab.com/)   ![GitHub commit activity](https://img.shields.io/github/commit-activity/t/JnliaH/chromaquant)   [![CQ Testing](https://github.com/JnliaH/ChromaQuant/actions/workflows/cq-test.yaml/badge.svg)](https://github.com/JnliaH/ChromaQuant/actions/workflows/cq-test.yaml)

<i>A solution for automated chromatography data analysis and reporting.</i>

<h3>Introduction</h3>
<img style="float: right;" align="right" width="256" alt="ChromaQuant Logo" src="https://github.com/JnliaH/ChromaQuant/blob/rebrand/images/ChromaQuantIcon.png">

`chromaquant` is an open-source toolkit designed to enable users to rapidly and precisely analyze chromatographic data. It offers tools for matching chromatographic signals to each other or to other tabulated data, writing formulas for dynamic Excel reporting, and peforming simple operations on tabulated data to produce properties like molecular weight.<br><br>

The development of `chromaquant` is associated with the <a href="https://www.rorrerlab.com/">Rorrer Lab</a> at the University of Washington Department of Chemical engineering.

<h3>Installation</h3>
<h4>Using pip</h4>

Install `chromaquant` in a Python environment by running the following command in the terminal/command prompt while that environment is active:

```bash
pip install chromaquant
```

<h4>Using uv</h4>

`chromaquant` can also be installed using `uv` by first creating a new project. For example, to create a new recipe project:

```bash
uv init cq-recipe
cd cq-recipe
```

To add ChromaQuant to the project, simply run:

```bash
uv add chromaquant
```

Please visit the official <a href="https://docs.astral.sh/uv/getting-started/">`uv` documentation</a> for more information on how to set up and execute projects.

<h3>Documentation</h3>

The official documentation for ChromaQuant is hosted by Read the Docs <a href="https://chromaquant.readthedocs.io/en/latest/">here</a>.
