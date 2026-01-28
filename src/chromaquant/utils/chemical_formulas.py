#!/usr/bin/env python
"""

COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

TOOLS FOR FILE IMPORTING AND EXPORTING

Julia Hancock
Started 1-16-2025

"""

from chemformula import ChemFormula

""" FUNCTIONS """


# Function to get the number of atoms of a given element from a formula
def get_number_element_atoms(formula: str | list,
                             element: str):

    # Try...
    try:
        # ...to split formula (checks if list or string)
        formula.split()

        # If it is a string, get a dictionary with
        # key:value pairs as element:number
        chemFormDict = ChemFormula(formula).element

        # Get the number of atoms of the passed element
        number_element_atoms = chemFormDict[element]

    # If an AttributeError occurs (formula is a list)...
    except AttributeError:

        # Create a new list to return
        number_element_atoms = []

        # For every formula within the list...
        for single_formula in formula:

            # Try...
            try:

                # Get a dictionary with key:value pairs as element:number
                chemFormDict = ChemFormula(single_formula).element

                # Get the number of atoms of the passed element from this
                # dictionary and append this to the return list
                number_element_atoms.append(int(chemFormDict[element]))

            # If there is a ValueError (e.g., formula contains None or NaN)...
            except ValueError:

                # Append zero
                number_element_atoms.append(0)

    return number_element_atoms


# Function to get the molecular weight from a chemical formula
def get_molecular_weight(formula: str | list):

    # Try...
    try:
        # ...to split formula (checks if list or string)
        formula.split()

        # If it is a string, get the weight
        weight = ChemFormula(formula).weight

    # If an AttributeError occurs (formula is a list)...
    except AttributeError:

        # Create a new list to return
        weight = []

        # For every formula within the list...
        for single_formula in formula:

            # Try...
            try:

                # Append the weight of the current formula
                weight.append(ChemFormula(single_formula).weight)

            # If there is a ValueError (e.g., formula contains None or NaN)...
            except ValueError:

                # Append zero
                weight.append(0)

    return weight
