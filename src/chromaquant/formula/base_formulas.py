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
def CREATE_FORMULA_FROM_STRING(formula_string,
                               formula_pointer):

    # If formula pointer is passed...
    if formula_pointer is not None:
        # Create Formula with pointer
        formula = Formula(formula_string, formula_pointer)

    # Otherwise...
    else:
        # Create Formula without pointer
        formula = Formula(formula_string)

    return formula


# Create formula for binary operations
def FORMULA_BINARY_OPERATION(pointer_1: dict[str, str],
                             pointer_2: dict[str, str],
                             operator: str,
                             formula_pointer: dict[str, str] = None):

    # Get a formula string
    formula_string = f'{pointer_1}{operator}{pointer_2}'

    # Get a Formula instance using CREATE_FORMULA_FROM_STRING
    formula = CREATE_FORMULA_FROM_STRING(formula_string, formula_pointer)

    return formula


# Create formula for binary addition
def FORMULA_ADDITION(pointer_1: dict[str, str],
                     pointer_2: dict[str, str],
                     formula_pointer: dict[str, str] = None):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(pointer_1,
                                       pointer_2,
                                       '+',
                                       formula_pointer)

    return formula


# Create formula for binary subtraction
def FORMULA_SUBTRACTION(pointer_1: dict[str, str],
                        pointer_2: dict[str, str],
                        formula_pointer: dict[str, str] = None):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(pointer_1,
                                       pointer_2,
                                       '-',
                                       formula_pointer)

    return formula


# Create formula for binary multiplication
def FORMULA_MULTIPLICATION(pointer_1: dict[str, str],
                           pointer_2: dict[str, str],
                           formula_pointer: dict[str, str] = None):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(pointer_1,
                                       pointer_2,
                                       '*',
                                       formula_pointer)

    return formula


# Create formula for binary division
def FORMULA_DIVISION(pointer_1: dict[str, str],
                     pointer_2: dict[str, str],
                     formula_pointer: dict[str, str] = None):

    # Get a Formula instance using FORMULA_BINARY_OPERATION
    formula = FORMULA_BINARY_OPERATION(pointer_1,
                                       pointer_2,
                                       '/',
                                       formula_pointer)

    return formula
