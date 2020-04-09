"""Define loan classes"""

from multiloan.utils import pay_loan, money_amount, compint
from warnings import warn
import pandas as pd
import numpy as np

class Loan:
    """
    Object containing information and data for a single loan.
    Default settings are for an annual rate, compounding daily, with monthly payments

    Parameters
    ----------
    principal: Loan balance
    rate: Interest rate for payment period
    payment: Payment per period
    n: Number of times interest compounds in pay period
    t: Payment frequency within rate compounding period
    stop: Stop criteria to avoid infinite calculation (default 1 million)

    Example: Annual interest rate of .05, compounding daily, paying monthly

    rate = .05
    n = 365 (compounding each day)
    t = 1/12 (Paying monthly, so a frequency of 1/12 per year)

    Functions
    -------
    pay_remaining(amount): Pay the remaining balance on loan, using `payment` as default or provide a custom `amount`
    pay_one(amount): Make a single payment using `payment` as default or provide a custom `amount`
    reset(): Reset payment history

    Properties
    ----------
    payments: A list of payments made on this loan
    balances: A list of balances after accruing interest and applying payments for each pay period
    totalpay: The total amount paid on this loan (ie. sum(payments))
    n_payments: The number of payments on this loan (ie. len(payments) - 1, to account for initial empty payment)
    """
    def __init__(self, principal: float, rate: float, payment: float=0, n: int=365, t: float=1/12, stop=1e6):

        self.principal = principal
        self.rate = rate
        self.payment = payment
        self.n = n
        self.t = t
        self.stop = stop

        # Initialize
        self.reset()

    def reset(self):
        """
        Reset payment loan payment history
        """
        self.payments = [0]
        self.balances = [self.principal]
        self.totalpay = 0
        self.n_payments = 0

    @property
    def balance(self):
        return self.balances[-1]

    def pay_remaining(self, amount=None):
        """
        Payment schedule for paying off remaining balance
        amount: `loan.payment` if none provided, else `amount` if provided
        """
        if not amount:
            amount = self.payment
        balances, payments = pay_loan(amount, self.balance, self.rate, self.n, self.t, self.stop)
        self.balances += balances
        self.payments += payments
        self.totalpay = sum(payments)
        self.n_payments = len(payments)

    def pay_one(self, amount=None):
        """
        Make a single payment to this loan after accruing interest for the payment period
        Default payment is set loan `payment`
        """
        if not amount:
            amount = self.payment
        # Calculate balance since last payment
        prev_balance = self.balances[-1]
        # Balance after accruing interest
        curr_balance = compint(prev_balance, self.rate, self.n, self.t)
        # Apply payment
        if curr_balance - amount > 0:
            curr_pay = amount
        # Otherwise, pay remaining
        else:
            curr_pay = curr_balance
        new_amount = curr_balance - curr_pay

        # Save
        self.payments.append(curr_pay)
        self.balances.append(new_amount)
        self.totalpay += curr_pay
        self.n_payments += 1


    def __repr__(self):
        rep = f"""\
Original principal: {money_amount(self.principal)}
Current balance: {money_amount(self.balance)}
Payment amount: {money_amount(self.payment)}
Total amount paid: {money_amount(self.totalpay)}
Number of payments: {self.n_payments}"""
        return rep

class MultiLoan:
    """
    A collection of loans. Pays off loans in order of interest rates while satisfying the minimum necessary payment
    for each loan.

    Assumes the same pay period for each loan
    """
    def __init__(self, Loans: list, payment: float):
        """
        Payment schedule for multiple Loans
        :param Loans: an array of Loan objects
        :param payment: Payment to contribute to all loans per pay period
        """
        self.Loans = Loans
        self._loan_dict = dict(enumerate(Loans))
        self.payment = payment

        # Initialize
        loan_df = self.get_loan_table()
        self.loan_df = loan_df
        self.reset()

        # Order loans by rate
        rate_order = loan_df.sort_values('rate', ascending=False).index

    def get_loan_table(self):
        """Create a table with principals, rate, and minimum for each loan"""
        data = [[loan.principal, loan.rate, loan.pament] for loan in self.Loans]
        table = pd.DataFrame(data, columns=['principal', 'rate', 'payment'])
        return table

    def reset(self):
        """
        Reset payment loan payment history
        """
        self.payments = [0]
        self.balances = [self.loan_df.payment.sum()]
        self.totalpay = 0
        self.n_payments = 0

    @property
    def balance(self):
        return self.balances[-1]

class Payrange:
    """
    Total payment associated with a range of loan payment values

    Calculate the total cost of paying off a loan for a range (from `low` to `high`) of period payments
    Addresses the question: "How much will I ultimately pay if I make a contribution of $X each pay period?"

    Parameters
    ----------
    loan: Either a single Loan or a MultiLoan
    payrange: A list of payment amounts

    Example:
    payrange = [100, 200, 300] will calculate the total cost of a loan at each of these monthly payments

    Properties
    ----------
    amounts: Amount of recurring payments assessed (exluces payment amounts that don't satisfy stop criteria)
    totals: A list of total amount paid at each level of `payrange`
    payments: A list of the number of payments at each level of `payrange`
    pct_change: A list of first difference percent change in `totals`
    df: A Pandas DataFrame of the above data
    """
    def __init__(self, loan: Loan, payrange: list):
        # Check Loan input
        if not any(isinstance(loan, t) for t in [Loan, MultiLoan]):
            raise TypeError('"loan" must either be a `Loan` or `MulitLoan` object')


        self.payrange = payrange
        # Get balances at each payrange level
        amounts = []
        totals = []
        payments = []
        for amt in payrange:
            # Reset loan
            loan.reset()
            # Payoff entirely with current amount
            try:
                loan.pay_remaining(amt)
            except AssertionError:
                warn('A payment amount was skipped because it surpassed stop criteria')
                continue
            amounts.append(amt)
            totalpay = loan.totalpay
            n_payments = loan.n_payments

            totals.append(totalpay)
            payments.append(n_payments)

        # Calculate percent change in total pays
        pct_changes = np.append(np.diff(totals), 0)/totals

        # Save
        self.amounts = amounts
        self.totals = totals
        self.payments = payments
        self.pct_change = pct_changes
        self.df = pd.DataFrame([[pr, tp, pc, np] for pr, tp, pc, np in
                                zip(amounts, totals, pct_changes, payments)],
                                        columns=['amount', 'total', 'pct_change', 'n_payments'])

    def __repr__(self):
        rep = f'Payrange(low={min(self.payrange)}, high={max(self.payrange)})'
        return rep
