.. _working-with-data:

Working with Data
===============================
.. testsetup:: *

    import chromaquant as cq

Many operations in ChromaQuant rely on :code:`DataSets`, which are objects that contain either
one- or two-dimensional data and offer various methods to collect, set, and manipulate these
data. The simplest DataSet available to users through the API is the :code:`Value` class, which
is used to instantiate objects that can each contain a singular datum. There is also a :code:`Table`
class, which stores two-dimensional data using the :code:`pandas.DataFrame` class.

Values
-------------------------------

This class is primarily targeted at users who wish to work with values like floats, integers, strings, and booleans.
A Value can be created like so:

.. code-block:: python

    my_value = cq.Value()

Data can be added to a Value in a few different ways. For one, data can be passed as an argument
during instantiation:

.. code-block:: python

    some_data = 14.6
    my_value = cq.Value(data=some_data)

Another way is to set the :code:`data` attribute directly:

.. code-block:: python

    new_data = 31.9
    my_value.data = new_data

The :code:`data` attribute also allows for getting and deleting its contents:

.. code-block:: python

    # Get the current data
    extracted_data = my_value.data
    # Delete the current data
    del my_value.data

Tables
-------------------------------

Tables behave very similarly in some aspects to Values (they are both children of the DataSet class, after all!). The
key difference is that Tables are intended to contain two-dimensional data. The Table class does this by leveraging the
extensive functionality offered by the :code:`pandas.DataFrame` class. We can create a Table in a similar way to a Value:

.. code-block:: python

    my_table = cq.Table()

We can assign data using either the :code:`data` argument or the :code:`data` attribute. First, we create a DataFrame using
pandas:

.. code-block:: python

    my_dictionary = {'Column A': [1, 2, 3], 'Column B': [4, 5, 6]}
    my_dataframe = pandas.DataFrame(my_dictionary)

Then, we can assign this dataframe to our Table:

.. code-block:: python

    # Assign using the data argument
    my_table = cq.Table(data=my_dataframe)
    # Reassign by setting the data attribute
    my_table.data = my_dataframe

As with Values, we can also get or delete data from Tables:

.. code-block:: python

    # Get the current data
    extracted_data = my_table.data
    # Delete the current data
    del my_table.data

Something else we can do with Tables is read our data directly from .csv files:

.. code-block:: python

    # Create a new table
    my_table = cq.Table()
    # Import the data from a .csv file
    my_table.import_csv_data('my_data.csv')

Back to our Example
-------------------------------

Let's return now to our scenario outlines in the previous page. Imagine we are given a sample of bergamot oil to analyze
on our GC-MS system. After injecting the sample in the instrument, acquiring data, and performing best hits analysis by
comparing collected mass spectra to library spectra, we have the following table of MS results:

=========== ==================== ======================= ========
Peak Number Retention Time (min) Compound                Formula
=========== ==================== ======================= ========
1           18.23                tricyclene              C10H16
2           18.81                α-thujene               C10H16
3           19.26                α-pinene                C10H16
4           20.12                camphene                C10H16
5           21.75                sabinene                C10H16
6           21.89                ß-pinene                C10H16
7           22.44                6-methyl-5-hepten-2-one C8H14O
8           22.61                myrcene                 C10H16
9           23.26                octanal                 C8H16O
10          23.31                α-phellandrene          C10H16
11          24.01                δ-3-carene              C10H16
12          24.21                α-terpinene             C10H16
13          24.89                p-cymene                C10H14
14          25.06                limonene                C10H16
15          25.13                1,8-cineole             C10H18O
16          25.36                (Z)-ß-ocimene           C10H16
17          26.00                (E)-ß-ocimene           C10H16
18          26.81                γ-terpinene             C10H16
19          27.09                cis-sabinene hydrate    C10H18O
20          27.78                octanol                 C8H18O
21          28.43                terpinolene             C10H16
22          29.11                linalool                C10H18O
23          29.34                nonanal                 C9H18O
24          29.72                heptyl acetate          C9H18O2
25          29.98                cis-limonene oxide      C10H16O
26          38.53                linalyl acetate         C12H20O2
27          54.49                ß-bisabolene            C15H24
=========== ==================== ======================= ========

We also get the following table of FID integration results:

=========== ==================== ===========
Peak Number Retention Time (min) Area
=========== ==================== ===========
1           18.24                9.642202419
2           18.79                721.0011595
3           19.30                2626.975549
4           20.10                80.28715918
5           20.36                13.20155492
6           21.71                2599.987859
7           21.90                16464.64891
8           22.48                9.540131909
9           22.61                2383.918994
10          23.22                67.72271269
11          23.27                84.84936771
12          24.04                11.54458953
13          24.23                381.0284691
14          24.88                954.0299001
15          25.02                79746.12728
16          25.10                32.72194488
17          25.33                92.3024417
18          25.48                8.178220039
19          25.97                476.8954081
20          26.85                17449.17202
21          27.11                94.59826749
22          27.76                20.20661954
23          28.41                746.6239539
24          29.15                23250.14097
25          29.39                79.28369498
26          29.71                7.280006075
27          29.83                3.327113495
28          30.01                22.03782356
29          38.51                66953.91378
30          54.47                1183.234388
=========== ==================== ===========

Let's start with the integration table. We can create a Table instance in Python by first adding our data to a DataFrame:

.. code-block:: python

    # Define a dictionary with our data as tabulated above
    fid_dictionary = {'Peak Number': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                                     16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
                     'Retention Time': [18.24, 18.79, 19.30, 20.10, 20.36, 21.71, 21.90, 22.48, 
                                        22.61, 23.22, 23.27, 24.04, 24.23, 24.88, 25.02, 25.10,
                                        25.33, 25.48, 25.97, 26.85, 27.11, 27.76, 28.41, 29.15,
                                        29.39, 29.71, 29.83, 30.01, 38.51, 54.47],
                     'Area': [9.642202419, 721.0011595, 2626.975549, 80.28715918, 13.20155492, 2599.987859
                              16464.64891, 9.540131909, 2383.918994, 67.72271269, 84.84936771, 11.54458953,
                              381.0284691, 954.0299001, 79746.12728, 32.72194488, 92.3024417, 8.178220039,
                              476.8954081, 17449.17202, 94.59826749, 20.20661954, 746.6239539, 23250.14097
                              79.28369498, 7.280006075, 3.327113495, 22.03782356, 66953.91378, 1183.234388]}

    # Create a DataFrame from the dictionary
    fid_dataframe = pandas.DataFrame(my_dictionary)

    # Create a Table with the data set to the DataFrame
    fid_table = cq.Table(data=fid_dataframe)

Alternatively, we could read the data directly from a .csv file if it is in that format. Let's do that with our MS data:

.. code-block:: python

    # Create a new table
    ms_table = cq.Table()
    # Import the data from a .csv file
    ms_table.import_csv_data('ms_data.csv')

Adding Complexity
-------------------------------

This is just the tip of the iceberg for these classes. There are several additional layers of functionality---including
formula assignment and reporting---that will be expanded upon further in the Getting Started section. Please continue on
to see how you can integrate this simple data manipulation in a more complex analysis.
