.. _petroleum-mixture:

Petroleum Mixture Example
===============================

The following is a demonstration using ``chromaquant`` to analyze a liquid petroleum mixture using gas chromatography. This example code is available in the repository at https://github.com/JnliaH/ChromaQuant.

Background
-------------------------------

Picture this: we have a unknown liquid mixture of petroleum species and we want to identify and quantify the species in this mixture using gas chromatography. We do know the exact quantity of an internal standard, 3-methylhexane, that we added to the liquid mixture. We have access to a GC-MS system and a software suite which together produce one table of integrated peak areas and one of species' identities with respect to retention time. We use an FID detector built into the GC-MS system for the integration values and the MS for the identities. We need to develop an analysis protocol to achieve the following:

1. Match the peak areas to the species identities.
2. Use response factors to calculate the mass of each identified species.
3. Produce a report with raw integration values and breakdowns by carbon number and compound type.

We can achieve this easily by writing a short recipe using ``chromaquant``. Let's do that now!

Recipe
-------------------------------

To start, we will need to import a few packages. Of course, we will need ``chromaquant``. But we will also need ``json`` and ``os`` to handle file configuration reading and path management, respectivley. We'll get to just what these packages are doing in a moment. For now, let's import them:

.. code-block:: python

    import chromaquant as cq
    import json
    import os

Now, let's define a function that will contain our analysis protocol. The first thing we want to do in this function is define all file paths relevant to our analysis.

.. code-block:: python

    def petroleum_mixture():

        # Get the file path
        file_path = os.path.dirname(os.path.abspath(__file__))
        # Get the example data path
        example_path = os.path.join(file_path, 'example_data')
        # Define paths for example data
        path_lq_FID_integration = \
            os.path.join(example_path, 'example_liquid_FID_integration.csv')
        path_lq_MS_components = \
            os.path.join(example_path, 'example_MS_components.csv')
        path_lq_FID_RFs = \
            os.path.join(example_path, 'example_FID_response_factors.csv')
        path_example_config = \
            os.path.join(example_path, 'example_config.json')
        path_report = \
            os.path.join(example_path, 'report.xlsx')

Here, we are creating path objects using ``os`` to make it easier for us to access the data we need. If your data takes a different form, or requires different path management, this is where you would edit this recipe! Let's now take a step back and look at our file structure::

    recipe/
    ├── petroleum-mixture.py
    └── example_data/
        ├── example_liquid_FID_integration.csv
        ├── example_MS_components.csv
        ├── example_FID_response_factors.csv
        ├── example_config.json
        └── report.xlsx

The file "example_liquid_FID_integration.csv" contains the table of integration values by retention time, while "example_MS_components.csv" contains the table of species' identities. Our "example_FID_response_factors.csv" file contains the response factors necessary to extract mass data from area data. Finally, the "example_config.json" file contains dictionaries that will be used in categorization. The "report.xlsx" is what will be created when the script is run.

Let's get some more configuration out of the way. First, let's define where in our report we would like the *top-left* corner of each DataSet to be:

.. code-block:: python

    # Define sheets for liquids
    liquid_sheet = 'Liquids Analysis'

    # Define starting cells for liquid tables and values
    liquid_table_cell = '$B$5'
    liquid_IS_area_cell = '$B$2'
    liquid_IS_mass_cell = '$C$2'
    liquid_breakdown_cell = '$P$5'
    liquid_2D_breakdown_cell = '$P$10'

You'll also notice we defined the name of the sheet we will be using. Let's import that categorization configuration now:

.. code-block:: python

    # Read example_config.json
    with open(path_example_config, 'r') as config_file:
        config_dict = json.load(config_file)

Great, now we have everything we need to start analyzing this data! The first thing we'll want to do is create our DataSets. These are objects that are going to contain our data and allow us to write formulas referencing our data. Let's start with our integration values:

.. code-block:: python

    # Create a table for integration results from a Flame Ionization Detector
    # signal collected when analyzing a liquid sample
    lq_FID_integration = cq.Table()
    # Read a .csv to add data to this table
    lq_FID_integration.import_csv_data(path_lq_FID_integration)

Here, we are creating a Table object to contain our integration values. Then, we're importing our .csv data directly into this Table object using the ``import_csv_data`` method. We can repeat this for our next two Tables:

.. code-block:: python

    # Create a table for a liquid components table from a Mass Spectrometer
    lq_MS_components = cq.Table()
    # Read a .csv to add data to this table
    lq_MS_components.import_csv_data(path_lq_MS_components)

    # Create a table for liquid response factors
    lq_FID_RF = cq.Table()
    # Read a .csv to add data to this table
    lq_FID_RF.import_csv_data(path_lq_FID_RFs)

Great, now we have somewhere to store all of our data! We now need to think about how we are going to calculate the mass of each species. As we hinted at earlier, we will be using an internal standard approach for our quantification. In short, this means that we will use response factors defined by the following equation:

.. math::

    RF_i = \frac{(A_i/A_s)}{(m_i/m_s)}

where :math:`A_i` is the area of a given species, :math:`A_s` is the area of our internal standard, :math:`m_i` is the mass of a given species, and :math:`m_s` is the mass of our internal standard. We can determine these response factors by creating and analyzing several mixtures of known amounts of each species of interest with our internal standard. We then extract the response factor :math:`RF_i` for a given species by applying a linear regression to the resulting data, where :math:`(A_i/A_s)` is the y-axis and :math:`(m_i/m_s)` is the x-axis.

In order for this approach to work, we'll need to store the area and mass of our internal standard. We can do this by creating two values:

.. code-block:: python

    # Create values for the internal standard area and mass
    IS_area = cq.Value(sheet=liquid_sheet,
                       start_cell=liquid_IS_area_cell,
                       header='Internal Standard Area')
    IS_mass = cq.Value(data=30,
                       sheet=liquid_sheet,
                       start_cell=liquid_IS_mass_cell,
                       )

You'll notice here that we are populating some additional parameters. We are adding the sheet (``liquid_sheet``) and cells (``liquid_IS_area_cell`` and ``liquid_IS_mass_cell``) where we want to report these values. We are also adding a header to the internal standard area value, though we'll skip that for ``IS_mass`` to demonstrate the difference in the report. We'll also set the ``data`` parameter in ``IS_mass`` to the known mass of our internal standard, 30 mg.

We only have a few more DataSets to create. We'll want one DataSet that will contain the combined peak information and our mass formulas. We'll also create our Breakdowns; see if you can track what arguments we are passing and why!

.. code-block:: python

    # Create a table for liquids analysis
    liquids_table = cq.Table(sheet='Liquids Analysis',
                             start_cell=liquid_table_cell)

    # Create a 1D breakdown by carbon number
    liquids_CN_breakdown = cq.Breakdown(liquid_breakdown_cell,
                                        'Liquids Analysis')

    # Create a 2D breakdown for liquids
    liquids_2D_breakdown = cq.Breakdown(liquid_2D_breakdown_cell,
                                        'Liquids Analysis')

Alright, now we're getting to the interesting part. We need to take the data in ``lq_FID_integration`` and match it to the data in ``lq_MS_components``. Luckily, though these tables are derived from different chromatograms (FID vs. MS), the detectors are at the end of the same column, so the peaks from each chromatogram are at nearly identical retention times. In short, we only need to compare the retention times for each entry in one table to the retention times for each entry in the other table. To do this, we'll first create a MatchConfig object to manage our matching procedure:

.. code-block:: python

    # Create a match configuration for liquids FID-MS
    match_config_lq_FIDpMS = cq.MatchConfig()

Simple enough, now let's add a match condition; this describes how we want the two datasets to be matched.

.. code-block:: python

    # Add a match condition
    match_config_lq_FIDpMS.add_match_condition(
        condition=cq.MatchConfig.IS_EQUAL,
        comparison=['RT', 'Component RT'],
        kwargs={'error': 0.05}
        )

Let's break this down. We are using the ``add_match_condition`` method to add our condition to our new MatchConfig. We define the ``condition`` parameter as the ``IS_EQUAL`` attribute, which is a method shorthand that means we want the items in the ``comparison`` list to be equal. We know that our retention times are not going to be exact, so we also want to specify an error margin within which we'll consider two retention times to be equivalent. We do this using the ``kwargs`` parameter, setting it to a dictionary containing our error value of 0.05 min.

The next step isn't strictly necessary for the matching to work, but helps with the final formatting for the report. We first will set the ``import_include_col`` attribute of our ``MatchConfig`` to a list of the columns we want to import from the second ``DataSet`` (which we will define later as the MS data). This allows us to avoid importing columns we don't want in our final report. We'll then use the ``output_cols_dict`` attribute to define the final column names for our report: we'll do this by defining a dictionary where each key is an old column name and each value is the new name for that column.

.. code-block:: python

    # Add columns to include from second DataFrame
    match_config_lq_FIDpMS.import_include_col = ['Component RT',
                                                 'Compound Name',
                                                 'Formula',
                                                 'Match Factor']

    # Specify which columns to output
    match_config_lq_FIDpMS.output_cols_dict = {'RT': 'FID RT (min)',
                                               'Area': 'Area',
                                               'Component RT': 'MS RT (min)',
                                               'Compound Name': 'Compound',
                                               'Formula': 'Formula',
                                               'Match Factor': 'Match Factor'}

There are likely going to be some cases where multiple peaks in one table are within the retention time window of the same peak in the other table. This means we may have multiple correct matches for the same table entry. We need to decide how we want these situations to be handled, and we can implement our preference using the ``multiple_hits_rule`` attribute. Let's say we want to choose the matching peak with the highest match factor, which is a measure of how well each recorded mass spectrum matches the mass spectrum of each peak's assigned compound. First, we'll set the ``multiple_hits_rule`` to ``SELECT_HIGHEST_VALUE``:

.. code-block:: python

    # Add a multple hits rule to select the lowest error
    match_config_lq_FIDpMS.multiple_hits_rule = \
        cq.MatchConfig.SELECT_HIGHEST_VALUE

Then, we'll select the column which will be evaluated using the multiple hits rule:

.. code-block:: python

    # Set the multiple hits rule column to the comparison column
    match_config_lq_FIDpMS.multiple_hits_column = 'Match Factor'

Amazing! Now all we need to do is match the data sets. To do this, we'll run the following lines of code:

.. code-block:: python

    # Match liquid FID and MS data
    lq_FIDpMS = lq_FID_integration.match(lq_MS_components.data,
                                         match_config_lq_FIDpMS)

    # Set results to liquids_table data attribute
    liquids_table.data = lq_FIDpMS

In the first line, we are getting a ``DataFrame`` (defined by `Pandas`) containing the results from matching the identities table to the integration table. We take one of our tables that will be the "core" data set, in this case the ``lq_FID_integration``, and use the ``match`` method. We pass the data stored in the identities table (``lq_MS_components.data``) as the first argument, and our matching configuration as the second argument. The line of code after that simply sets the data attribute of our new ``liquids_table`` to the resulting ``DataFrame``.

Alright, now we have our data sets fully matched. In order to move forward with our quantification, we'll need to add some additional data to each row in the ``liquids_table``. Specifically, we'll need to know the carbon number and molecular weight of each species. We'll be using these values in the following steps, but for now let's populate our new columns:

.. code-block:: python

    # Add a carbon number count column
    liquids_table.add_element_count_column('Formula', 'C', 'Carbon Number')

    # Add a molecular weight column
    liquids_table.add_molecular_weight_column('Formula', 'Molecular Weight')

``Tables`` in ``chromaquant`` have some useful column population methods that make this a piece of cake. First, we have the ``add_element_count_column`` method, which takes the name of a column containing molecular formulas, the elemental symbol to count (in our case, 'C' for 'Carbon'), and the name to give the new column containing the count of that element. We also have the ``add_molecular_weight_column`` method, which will determine the molecular weight of each entry in the column given in the first argument. It will store the results in a new column with the name provided in the second argument.

Now that we have these additional columns, we need to go about assigning response factors to each of our identified species. Recall that we have a table of response factors organized by compound name. We can assign the appropriate response factors using the ``Match`` module just like we did to match FID data to MS data (even though we are now comparing compound names instead of retention times, so ``Match`` works for ``strings`` as well as ``floats``!). We'll write this one out in its entirety below, see if you can follow the logic!

.. code-block:: python

    # Create a match configuration for liquid response factors
    match_config_lq_RF = cq.MatchConfig()

    # Add a match condition
    match_config_lq_RF.add_match_condition(condition=cq.MatchConfig.IS_EQUAL,
                                           comparison='Compound')

    # Add columns to include from second DataFrame
    match_config_lq_RF.import_include_col = ['Sample Set', 'Response Factor']

    # Match response factors to liquids FIDpMS
    liquids_table.data = liquids_table.match(lq_FID_RF.data,
                                             match_config_lq_RF)

Unfortunately, as is often the case with complex petroleum mixtures, we may not have response factors developed for every species of interest. There are several ways to work around this, but one approach is to assign response factors using an experimentally derived formula that relates response factors to some observable property. In our case, let's say we have a formula that gives estimated response factors by carbon number:

.. math::

    RF_i = 0.0000496 \cdot CN^3 - 0.003 \cdot CN^2 + 0.0506 \cdot CN + 0.731

We can write a block of code to assign response factors to all species that do not already have one by first writing our formula in Python:

.. code-block:: python

    # Define a function for assigning interpolated response factors
    def RF_by_carbon_number(CN):
        return 0.0000496*CN**3 - 0.003*CN**2 + 0.0506*CN + 0.731

This function will return an estimated response factor using a passed carbon number. We can then loop through every row in the table, assigning estimated response factors as needed:

.. code-block:: python

    # For every row in the liquids data...
    for i, row in liquids_table.data.iterrows():

        # If the Response Factor is None...
        if row['Response Factor'] is None:

            # Get the carbon number
            CN = row['Carbon Number']

            # If the carbon number is not zero...
            if CN != 0:

                # Get an interpolated response factor
                RF = RF_by_carbon_number(CN)

                # Set the row's response factor to RF
                liquids_table.data.at[i, 'Response Factor'] = RF

                # Set the row's Sample Set to Interpolated
                liquids_table.data.at[i, 'Sample Set'] = 'Interpolated'

            # Otherwise, pass
            else:
                pass

        # Otherwise, pass
        else:
            pass

In this block, we are looping through the ``liquids_table`` ``DataSet`` directly using the `Pandas` ``iterrows`` method. For every row, if that row does not have a response factor (i.e., it was not given one in the previous matching step) and the carbon number is not zero, an estimated response factor will be generated. That row's 'Response Factor' entry will then be set to this returned value, and the 'Sample Set' entry set to 'Interpolated' (The 'Sample Set' column is used to track the origin of our response factors and is dervied mainly from our earlier RF matching).

It is very common in petroleum analytics to lump species into easily recognizable groups. For example, species can be lumped according to their functional groups (e.g., linear alkanes, aromatics, alkenes, etc.). We can assign compound types like these easily using the ``Categories`` module. To start, we'll create a new ``Categories`` instance:

.. code-block:: python

    # Create new Categories instance
    hydrocarbon_categories = cq.utils.Categories()

A ``Categories`` object can be used when there are shared or similar features of two different data points that can be easily reduced to an equivalence check. If we take a peek at the ``config_file`` from earlier, this becomes easier to understand::

    {
        "L": ["methane","ethane","propane","butane",
              "pentane","hexane","heptane","octane",
              "nonane","decane","undecane","hendecane",
        ...],

        "B": ["iso","neo","methyl","ethyl","propyl","butyl","pentyl",
              "hexyl","heptyl","octyl","nonyl","decyl","undecyl"
        ...],

        ...
    }

Above is a snippet from the ``config file`` showing a dictionary with single-letter keys and values set to lists of compound name components. Let's now further define what these keys represent in our Python recipe:

.. code-block:: python

    # Get a dictionary of abbreviations and compound types
    compound_type_dict = {'A': 'Aromatics',
                          'E': 'Alkenes',
                          'C': 'Cycloalkanes',
                          'B': 'Branched Alkanes',
                          'L': 'Linear Alkanes'}

Based on this dictionary, we can say that the 'L' and 'B' in ``config_file`` are equivalent to 'Linear Alkanes' and 'Branched Alkanes', respectively. Let's finish this block of code before we dive into an explanation of ``Categories``:

.. code-block:: python

    # Add categories for each compound type
    for abbreviation in compound_type_dict:
        hydrocarbon_categories[compound_type_dict[abbreviation]] = \
            config_dict[abbreviation]

    # Set the categorizer function
    hydrocarbon_categories.categorizer = hydrocarbon_categories.IS_IN

    # Add compound types to the liquids table
    liquids_table.add_category_column('Compound',
                                      hydrocarbon_categories,
                                      'Compound Type')

Here, we are looping through each key in the ``compound_type_dict``. For every key (i.e., compound abbreviation), we are adding an entry into the ``Categories`` object with the full compound type as the key and the respective ``config_dict`` list as the value. We can assign category lists directly like this because ``Categories`` acts as an alias for its inner stored dictionary whenever it is used like a dictionary. We are then setting the categorizer function to ``IS_IN``, which means that we want to assign a compound type to a compound if it contains at least one substring from that compound type's ``config_dict`` value list.

It is important to note that ``Categories`` is order sensitive, so the categorizer function will loop through each compound type as it is ordered and assign the first one that has a matching substring. For example, the compound '2-methyloctane' could fall under either 'Branched Alkanes' or 'Linear Alkanes' according to our categories, but the categorizer will assign it to 'Branched Alkanes' because this category is ordered sooner in the ``Categories`` dictionary than 'Linear Alkanes'. In our example, the order is being determined by the definition of ``compound_type_dict`` (i.e., A -> E -> C -> B -> L). We can add a column to the ``liquids_table`` based on our ``Categories`` object using the ``add_category_column`` method as above. The first parameter is the name of the column to base the categories off of, the second is the ``Categories`` object, and the third the name of the column to output categories to.

That was a lot to accomplish in only a few lines of code! Now we can move on to getting our report ready. To do this, we will need to create a new ``Results`` object and add all of the data we have processed so far to it.

.. code-block:: python

    # Define Results instance for liquids analysis
    liquids = cq.Results()

    # Add the liquids table
    liquids.add_table(liquids_table)

    # Add the internal standard values
    liquids.add_value(IS_area)
    liquids.add_value(IS_mass)

    # Add the liquids carbon number breakdown
    liquids.add_breakdown(liquids_CN_breakdown)

    # Add the liquids 2D breakdown
    liquids.add_breakdown(liquids_2D_breakdown)

Notice that there are separate methods for adding ``Values``, ``Tables``, and ``Breakdowns``. This is important because each of these ``DataSets`` will be managed and exported to the report slightly differently. With this out of the way, we can get to possibly the most exciting part of our recipe: our dynamic formulas! Recall that we need to get the area under the internal standard peak in order to complete our quantification. Breaking this down, we need to find the row associated with our internal standard in the ``liquids_table`` and then set our ``IS_area`` value to the area listed in that row. To do this in Excel, we would use the following formula::

    =INDEX({column containing areas}, MATCH({internal standard name}, {column containing compound names}, 0))

Let's write this in Python using a few tricky methods:

.. code-block:: python

    # Create a formula string for the area cell
    IS_area_formula_string = (f"=INDEX({liquids_table.insert('Area')}, MATCH("
                              f'"Hexane, 3-methyl-", '
                              f"{liquids_table.insert('Compound')}, 0))")

Here, we have written the formula out using a multiline f-string. We can see the general structure, including the name of our internal standard, but notice what we have put in place of {column containing areas} and {column containing compound names}. We have written the table containing our data followed by the ``insert`` method, to which we pass either the 'Area' key or the 'Compound key'. The ``insert`` method allows you to insert a reference to a specific value or a specific column within a table directly into a formula string. This string will then be independently processed any time a report is generated by the ``Results`` class. No more keeping track of exactly which cells contain what in Excel!

This is a string representation of the formula, but we actually need to create a ``Formula`` object in order to make use of this functionality. We can do this in a couple of lines:

.. code-block:: python

    # Create a Formula instance for the area cell
    IS_area_formula = cq.Formula(IS_area_formula_string)

    # Add pointers to Formula
    IS_area_formula.point_to(IS_area.id)

Here we are defining a new formula, ``IS_area_formula``, by passing our formula string to a new instance of ``Formula``. We are then using the ``point_to`` method to tell the ``Formula`` exactly where we want this new formula to be located (in our case, the ``Value`` we have set up to contain this formula). Note that we need to use the ``id`` attribute of our ``Value`` here. You can actually pass the pointer (e.g., ``IS_area.id``) directly to the ``Formula`` during initializationm, and can write the formula string directly as an argument too, which can shorten the number of lines of code if that is your preference! Let's now add our new formula to our ``Results`` object.

.. code-block:: python

    # Add the area cell Formula to liquids analysis
    liquids.add_formula(IS_area_formula)

Now we have our first formula! We now need to calculate the ratio of the area of each species of interest to the area of the internal standard. We could write the formula out like we did before, but we can also use some shortcut base formulas that are default in ``ChromaQuant``. Let's write out the formula in this way:

.. code-block:: python

    # Create an area ratio Formula
    area_ratio_formula = cq.formula.FORMULA_IF_ERROR(
        cq.formula.FORMULA_DIVISION(
            liquids_table.insert('Area'),
            IS_area.insert()
        )
    )

    # Add pointers to Formula
    area_ratio_formula.point_to('Ai/As', liquids_table.id)

    # Add the area ratio Formula to the liquids analysis
    liquids.add_formula(area_ratio_formula)

Here we're using the ``FORMULA_IF_ERROR`` and ``FORMULA_DIVISION`` functions provided in the ``Formula`` module. Starting with the inner formula, we are passing the area column reference in the first argument and the internal standard area reference in the second. We are then wrapping this entire division formula in the ``FORMULA_IF_ERROR`` function, and setting the result to our new ``Formula`` instance variable. It is worth noting some of the implied behavior of each of these functions before moving on. There is an issue that arises when performing operations between some data that cover a range and some that are individual values: how exactly do we handle formulas where we want to reference an entire range? What if instead we want a resulting column to refer to each respective value of the dependent range? By default, referencing a column in a formula will lead to that formula referencing each respective value in that column if the ``Formula`` is pointing to a new column, and will reference the entire range if the ``Formula`` is pointing to an individual value. This behavior can be altered by passing either ``True`` or ``False`` as a second argument (or as a keyword argument with ``range=``) to the ``insert`` method.

Alright, only one more formula to go! It's shown below, but go ahead and try to break it down yourself. As one important note, whenever a base formula is nested inside another base formula, the nested formula's ``formula_string`` attribute must be used. This is because base formulas (except for ``FORMULA_IF_ERROR``) only accept strings, not ``Formula`` objects. We can also pass a key and table pointer directly to a base formula (except for ``FORMULA_IF_ERROR``) to skip the secondary ``point_to`` step.

.. code-block:: python

    # Create a mass Formula
    mass_formula = cq.formula.FORMULA_IF_ERROR(
        cq.formula.FORMULA_MULTIPLICATION(
            IS_mass.insert(),
            cq.formula.FORMULA_DIVISION(
                liquids_table.insert('Ai/As'),
                liquids_table.insert('Response Factor')
            ).formula_string,
            'Mass (mg)',
            liquids_table.id
        )
    )

    # Add the mass Formula to the liquids analysis
    liquids.add_formula(mass_formula)

Alright, we're on the home stretch! We just need to add our breakdowns and then report the results. We'll start by creating our 1D breakdown:

.. code-block:: python

    # Define carbon numbers to cover
    CN_range = [1, 2, 3, 4, 5, 6, 7, 8]

    # Create a 1D carbon number breakdown
    liquids_CN_breakdown.create_1D(liquids_table,
                                   'Carbon Number',
                                   'Mass (mg)',
                                   CN_range)

Here, we are creating a 1D breakdown within our ``liquids_CN_breakdown`` by using the ``create_1D`` method. This method accepts a ``Table`` to base the breakdown on, a name of the column to organize the breakdown by, the name of the column to conditionally aggregate, and an optional list of values that may or may not show up in the organizing column to be used in the final breakdown. We can do a similar thing for our 2D breakdown using the ``create_2D`` method:

.. code-block:: python

    # Create a 2D carbon number-compound breakdown
    liquids_2D_breakdown.create_2D(liquids_table,
                                   'Compound Type',
                                   'Carbon Number',
                                   'Mass (mg)',
                                   {'Carbon Number':
                                    CN_range,
                                    'Compound Type':
                                    list(compound_type_dict.values())})

Here we are passing the ``liquids_table`` in the first argument, then passing the names of the first and second columns to organize by in the following arguments. In the fourth argument, we put the name of the column to conditionally aggregate, and in the final argument we pass a dictionary. In this dictionary we specify allowable organization values just like we did in the 1D example, except this time specifying limits for each organizing column, giving each column name as the keys and their respective ranges as the values. We can reuse our ``CN_range`` and ``compound_type_dict`` from before.

You may have noticed that we only provided headers for some of these ``DataSets`` and not for others. This was actually so we could demonstrate the dynamic nature of reporting parameters like headers in ``chromaquant``. If we, after our entire recipe, decide to add headers to some of the ``DataSets`` we skipped, we can do it like so:

.. code-block:: python

    # Try to change the header of the breakdown
    liquids_2D_breakdown.header = 'Distribution Matrix'

    # Change the header of the liquids analysis table
    liquids_table.header = 'Liquids Analysis'

    # Change the header of the internal standard mass
    IS_mass.header = 'Internal Standard Mass (mg)'

    # Change the header of the 1D breakdown
    liquids_CN_breakdown.header = 'Carbon Number Breakdown'

The reason this feature is so valuable is because changing the presence or abscence of a header, the starting cell of a ``DataSet``, or the ``DataSets`` each formula will point to can significantly change the actual placement of ``DataSets`` in the report. By managing it using a dynamic ``Results`` object, we can change all of these variables and have the report immediately reflect these changes without needing to manually alter sheet names and cell references.

We can wrap up our recipe by reporting the results to the path we defined earlier:

.. code-block:: python

    # Export the results to .csv
    liquids.report_results(path_report)

Ta-da, we made it! In only a few hundred lines of code, we were able to write a recipe that we can use to automatically analyze and report as many liquid petroleum samples as we need. This example highlighted a few key features of ``chromaquant``, but also showed some more tricky solutions needed to solve certain analytical needs. You can see the full workflow and the resulting report by running this example yourself, which you can download from the repository. We hope this example explanation was valuable to you, and good luck writing a recipe of your own!