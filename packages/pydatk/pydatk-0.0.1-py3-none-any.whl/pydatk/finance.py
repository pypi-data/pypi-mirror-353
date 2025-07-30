"""Finance tools and calculators.

This module contains tools for handling financial data, including common
financial calculations such as effective interest rate and future value.
"""

def effective_rate(nom, nper):
    """Calculates effective interest rate from a given nominal rate and
    number of compounding periods.

    :param nom: Nominal interest rate as a decimal (e.g. 0.05 for 5%).
    :type nom: float
    :return: The result of the following calculation: 
        effective rate = (1 + (nom / nper)) ^ nper - 1
    :rtype: float
    """
    return float((1 + (nom / nper)) ** nper - 1)