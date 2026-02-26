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

Adding Complexity
-------------------------------

This is just the tip of the iceberg for these classes. There are several additional layers of functionality---including
formula assignment and reporting---that will be expanded upon further in the Getting Started section. Please continue on
to see how you can integrate this simple data manipulation in a more complex analysis.
