What can ChromaQuant do for me?
===============================
.. testsetup:: *

    import chromaquant
    import pandas

ChromaQuant is designed to enable users to create custom analysis recipes for complex
chromatography datasets. To this end, ChromaQuant offers several modules with unique
functionality that can be leveraged by users to perform various operations on their
datasets.

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
