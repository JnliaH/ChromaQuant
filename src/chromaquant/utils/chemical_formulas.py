#!/usr/bin/env python
"""

The Chemical Formulas submodule contains functions that allow the user to
extract information out of chemical formulas (e.g., molecular weight).

"""

from chemformula import ChemFormula

""" FUNCTIONS """


# Function to get the number of atoms of a given element from a formula
def get_number_element_atoms(formula: str | list[str],
                             element: str) -> list[int] | int:

    # Try...
    try:
        # ...to split formula (checks if list or string)
        formula.split()

        # If it is a string, get a dictionary with
        # key:value pairs as element:number
        chemFormDict = ChemFormula(formula).element

        # Get the number of atoms of the passed element
        number_element_atoms: int | list[int] = chemFormDict[element]

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
def get_molecular_weight(formula: str | list[str]) -> float | list[float]:

    # Try...
    try:
        # ...to split formula (checks if list or string)
        formula.split()

        # If it is a string, get the weight
        weight: float | list[float] = ChemFormula(formula).formula_weight

    # If an AttributeError occurs (formula is a list)...
    except AttributeError:

        # Create a new list to return
        weight = []

        # For every formula within the list...
        for single_formula in formula:

            # Try...
            try:

                # Append the weight of the current formula
                weight.append(ChemFormula(single_formula).formula_weight)

            # If there is a ValueError (e.g., formula contains None or NaN)...
            except ValueError:

                # Append zero
                weight.append(0)

    return weight
