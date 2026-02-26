.. _results-getting-started:

Implementing the Results Class
===============================
.. testsetup:: *

    import chromaquant as cq

The utility of ChromaQuant is not immediately apparent from the previous section on the Value and
Table classes. After all, 1D and 2D data manipulation is already well established in Python! The
key point here is that ChromaQuant's main usefulness comes not from extant data manipulation tools,
but from the integration of these tools with novel dynamic formula development and reporting specific
to chromatography applications. This is partially enabled through the :code:`Results class`.

We can create a Results instance as follows:

.. code-block:: python

    my_results = cq.Results()