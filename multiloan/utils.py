import numpy as np


def compint(P, r, n, t) -> float:
    """
    Compute the compounding interest
    P: principal
    r: interest rate
    n: number of times interest compounds in period
    t: Number of time periods

    A = P (1 + r / n) ^ (n * t)
    """
    A = P * np.power(1 + r / n, n * t)
    return A

def payment_amount(balance, payment):
    """
    The amount of a payment given a balance is which ever is less
    """
    curr_payment = min(balance, payment)
    return curr_payment

def single_payment(payment, P, r, n=365, t=1/12):
    """
    Make a single payment on a loan after accruing interest for the provided pay period
    :param payment: Payment amount per period
    :param P: principal
    :param r: interest rate
    :param n: number of times interest compounds in period
    :param t: payment frequency
    :return: (new principal, amount paid)
    """
    # Calculate new principal at end of period
    P = compint(P, r, n, t)
    ## Subtract payment
    # Pay payment amount until principal is zero
    curr_pay = payment_amount(P, payment)
    P -= curr_pay

    # Round
    curr_pay = round(curr_pay, 2)
    P = round(P, 2)
    return P, curr_pay

def pay_loan(payment, P, r, n=365, t=1/12, stop=1e6) -> tuple:
    """
    Pay a compound interest loan to extinction
    Default parameters for daily compounding with monthly payments
    :param payment: Payment amount per period
    :param P: principal
    :param r: interest rate
    :param n: number of times interest compounds in period
    :param t: payment frequency
    :param stop: Stop criteria to avoid infinite calculation (default 1 million)
    :return: (balances, payments)
    | balances: balances for each period
    | payments: payments for each period
    """
    # Keep track of balances after each payment
    balances = []
    payments = []
    while P > 0:
        P, curr_pay = single_payment(payment, P, r, n, t)
        assert P <= stop, f'Payments of {money_amount(payment)} have led the balance to reach stopping criteria of' \
                          f' {money_amount(stop)}.'
        balances.append(P)
        payments.append(curr_pay)
    return balances, payments

def money_amount(x: float) -> str:
    """
    Convert a float to a string dollar amount with commas
    Ex. 1000.235 -> $1,000.24
    """
    # Round to hundreds
    rounded = '%.2f' % x
    # Split into dollars and cents
    dollars, cents = rounded.split('.')

    # Add commas every three digits to dollars
    rev_dollars = ''
    count = 0
    for i in dollars[::-1]:
        rev_dollars += i
        count += 1
        # Add comma
        if count == 3:
            rev_dollars += ','
            count = 0

    # Flip reversed representation
    ref_dollars = rev_dollars.rstrip(',')[::-1]

    # Final format
    ref_amt = f'${ref_dollars}.{cents}'
    return ref_amt

