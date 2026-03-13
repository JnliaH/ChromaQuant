.. _starting-with-example:

Starting with an Example
===============================
.. testsetup:: *

    import chromaquant as cq

To fully demonstrate the power of ChromaQuant, let's define an example scenario we can work through as
we explore each module within the package.\ [1]_

Imagine we are a company that performs routine analyses of the components in various perfumes. We are often
provided samples with dozens or hundreds of individual components which we need to identify and quantify for
our customers. To perform these analyses, we have access to the following:

- A single GC-MS with which we can effectively separate all components. In addition to the MS detector,
  our instrument has an flame ionization detector (FID).
- A commercial software that can compare mass spectra against a coupled mass spectral library, returning top
  matches by retention time.
- Another commercial software that identifies and integrates peaks within collected FID chromatograms.

In order to analyze any given sample to our customers' satisfaction, we need to perform the following steps:

1. Extract the table of integration values from the FID analysis and the table of top compound matches from
   the MS analysis, each ordered by retention time.
2. Match the FID and MS data by retention time.
3. Apply the external standard approach to quantify the integration values using previously collected response
   factors.
4. Report the results in a customer-friendly way.

With this scenario in mind, let's take a closer look at how we can use the Data module to organize our data.

.. [1] The example in subsequent sections is based on an article by Verzera et al.\ [2]_ Data presented, such as retention times and
       integration values, are approximated based on the chromatograms and tables presented in the article. The
       components identified in the sample of bergamot oil are taken from the list of components.
.. [2] Verzera, A.; Lamonica, G.; Mondello, L.; Trozzi, A.; Dugo, G. The Composition of Bergamot Oil. Perfumer and
       Flavorist 1996, 21, 19–42.
