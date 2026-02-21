.. _what-can-cq:

What can ChromaQuant do for me?
===============================
.. testsetup:: *

    import chromaquant
    import pandas

ChromaQuant is designed to enable users to create custom analysis recipes for complex
chromatography datasets. To this end, ChromaQuant offers several modules with unique
functionality that can be leveraged by users to perform various operations on their
datasets.

Storing and Manipulating Datasets
----------------------------------

The module most users will interact with is the Data module, which contains classes
that describe how users can store, modify, and report datasets. There are two main
classes, :code:`Value` and :code:`Table`, which allow for the storage of single or
multiple data points, respectively. Values are intended to store integers,
strings, or other single-value data. Tables, on the other hand, store a :code:`pandas.DataFrame`
with a 2D data hierarchy. The :code:`pandas` package, having one of the most extensive
data storage API's of any Python package, can be leveraged as desired by users by simply
referring to the Table's :code:`data` attribute.

For example, we can create a Table and assign it a DataFrame with some data:

.. code-block:: python

    my_dictionary = {'Column A': [1, 2, 3], 'Column B': [4, 5, 6]}
    my_dataframe = pandas.DataFrame(my_dictionary)
    my_table = chromaquant.Table(data=my_dataframe)

We can then access a value directly using the :code:`pandas.DataFrame.at` method on the Table's :code:`data` attribute:

.. doctest::

    >>> print(my_table.data.at['Column B', 1])
    5

The purpose of the Table class is to wrap all of the attributes and methods of DataFrame with
additional methods, such as those that add new column manipulation and addition functionality
or those that enable object mediation and formulaic reporting. The purpose of Value is the same,
but without containing references to additional functionality through pandas.

Matching Datasets
-------------------------------

Many users may also find the :code:`Match` module useful. This module (and its associated method
within the Table class) enables users to match data from two different Tables according to a
customizable :code:`MatchConfig` instance.

Adding Dynamic Excel Formulas
-------------------------------

A major strength of the ChromaQuant API is its formula creation functionality. There exist
countless open-source packages that enable users to perform Pythonic operations on datasets
for various applications across many domains (e.g, science, statistics, LLMs). However, these
packages generally operate directly on data and output results without the formula being
directly accessible within any reports that are created. ChromaQuant leverages the formula
system used in Excel workbooks to create formulaic representations of user-defined operations
that can then be immediately viewed, modified, or fixed in created reports.

Reporting
-------------------------------

On the topic of reports, ChromaQuant also leverages the Excel reporting support provided by
both :code:`pandas` and :code:`openpyxl` to facilitate reporting operations that are common
is chromatography. Datasets (e.g., Tables or Values) can be exported directly to Excel this
way by specifying the desired worksheet and output cell(s). Using the :code:`Breakdown` class
in the Data module, users can also conditionally aggregate columns in Tables using Excel formulas
like SUMIFS or COUNTIFS and report formulas directly, avoiding the somewhat opaque Python-based
aggregation alternative.

And...?
-------------------------------

ChromaQuant is being continually developed and having additional features and fixes added
all the time. If you are interested in seeing more features added to ChromaQuant, please
voice your idea in the official `GitHub Issues <https://github.com/JnliaH/ChromaQuant/issues>`__ page! We are very interested
in expanding the applications of this tool to new domains in chromatography and welcome any and all feedback.

Please continue on through the Getting Started section to learn more about how you can apply ChromaQuant in your analysis workflow!