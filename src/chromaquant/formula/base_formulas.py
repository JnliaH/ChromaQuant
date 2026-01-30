#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COPYRIGHT STATEMENT:

ChromaQuant – A quantification software for complex gas chromatographic data

Copyright (c) 2026, by Julia Hancock
              Affiliation: Dr. Julie Elaine Rorrer
              URL: https://www.rorrerlab.com/

License: BSD 3-Clause License

---

COLLECTION OF SIMPLE FORMULAS

Julia Hancock
Started 01-23-2026

"""

from .formula import Formula

""" FUNCTIONS """


# Create formula using formula string and (optionally) pointer
def CREATE_FORMULA_FROM_STRING(formula_string: str):

    # Create Formula without pointer
    formula = Formula(formula_string)

    return formula


# Create formula by wrapping existing formula in stated Excel formula
def WRAP_FORMULA_STRING(inner_formula_string, wrapping_formula_string):

    # Get a new formula string
    formula_string = \
        f'={wrapping_formula_string}({inner_formula_string})'

    return formula_string


# Wrap existing formula in IFERROR()
def FORMULA_IF_ERROR(formula: Formula):

    # Get the formula string
    formula_string = formula.formula_string

    # If there is an equals sign at the beginning...
    if formula_string[0] == '=':
        # Remove the equals sign
        formula_string = formula_string[1:]

    # Otherwise, pass
    else:
        pass

    # Wrap the formula string in IFERROR()
    formula_string = '=IFERROR(' + formula_string + ', "")'

    # Set the formula string in Formula again
    formula.formula_string = formula_string

    return formula


# Create formula for binary operations
def FORMULA_BINARY_OPERATION(left_hand_side: str,
                             right_hand_side: str,
                             operator: str):

    # Get a list of sides
    side_list = [left_hand_side, right_hand_side]

    # For each passed side of the operator...
    for i in range(len(side_list)):

        # If the side starts with equals...
        if side_list[i][0] == '=':
            # Remove the equals sign
            side_list[i] = side_list[i][1:]

        # Otherwise, pass
        else:
            pass

    # Get a formula string
    formula_string = f'=({side_list[0]}{operator}{side_list[1]})'

    # Get a Formula instance using CREATE_FORMULA_FROM_STRING
    formula = CREATE_FORMULA_FROM_STRING(formula_string)

    return formula


# Create formula for binary addition
def FORMULA_ADDITION(left_hand_side: str,
                     right_hand_side: str):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(left_hand_side,
                                       right_hand_side,
                                       '+')

    return formula


# Create formula for binary subtraction
def FORMULA_SUBTRACTION(left_hand_side: str,
                        right_hand_side: str):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(left_hand_side,
                                       right_hand_side,
                                       '-')

    return formula


# Create formula for binary multiplication
def FORMULA_MULTIPLICATION(left_hand_side: str,
                           right_hand_side: str):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(left_hand_side,
                                       right_hand_side,
                                       '*')

    return formula


# Create formula for binary division
def FORMULA_DIVISION(left_hand_side: str,
                     right_hand_side: str):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(left_hand_side,
                                       right_hand_side,
                                       '/')

    return formula
