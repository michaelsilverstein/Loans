"""Define loan classes"""

from multiloan.utils import pay_loan, money_amount, single_payment, payment_amount
from warnings import warn
import pandas as pd
import numpy as np
from typing import List, Union


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
    t: Payment period within rate compounding period
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
    df: A pandas DataFrame of payments and balances
    """

    def __init__(self, principal: float, rate: float, payment: float = 0, n: int = 365, t: float = 1 / 12, stop=1e6):

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
        self._payments = [0]
        self._balances = [self.principal]

    @property
    def balance(self):
        return self._balances[-1]

    @property
    def totalpay(self):
        return sum(self._payments)

    @property
    def n_payments(self):
        return len(self._payments) - 1

    @property
    def payments(self):
        return np.array(self._payments)

    @property
    def balances(self):
        return np.array(self._balances)

    @property
    def df(self):
        """DataFrame of payment history"""
        data = [{'amount': p, 'balance': b, 'payment': i} for p, b, i in zip(self._payments, self._balances, range(self.n_payments))]
        return pd.DataFrame(data)


    def pay_remaining(self, amount=None):
        """
        Payment schedule for paying off remaining balance
        amount: `loan.payment` if none provided, else `amount` if provided
        """
        if not amount:
            amount = self.payment
        balances, payments = pay_loan(amount, self.balance, self.rate, self.n, self.t, self.stop)
        self._balances += balances
        self._payments += payments

    def pay_one(self, amount=None):
        """
        Make a single payment to this loan after accruing interest for the payment period
        Default payment is set loan `payment`
        """
        if not amount:
            amount = self.payment
        # Apply single payment
        new_amount, curr_pay = single_payment(amount, self.balance, self.rate, self.n, self.t)

        # Save
        self._payments.append(curr_pay)
        self._balances.append(new_amount)

    def __repr__(self):
        rep = f'Loan(original={money_amount(self.principal)}, balance={money_amount(self.balance)})'
        return rep

    def __str__(self):
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

    Loans can be provided a list of `Loan` objects or as a file path to a CSV with columns for the prinicipal, rate,
    and payment for each loan.

    Only a list of loans or a filepath can be provided

    Parameters
    ----------
    Loans: an array of Loan objects
    payment: Payment to contribute to all loans per pay period
    filepath: Path to CSV file containing the principal, rate, and payment for each loan, one loan per line.
        By default, it is assumed that the column names are 'principal', 'rate', and 'payment' respectively.
        *Make sure there are NO STRING CHARACTERS in this file (ex. no '$' or ',')
        *Rates must be provided as DECIMALS, not percents (ex. 5% must be provided as .05)
    {principal, rate, payment}_col: Name of column in file at `filepath` indicating each loan feature
    load_kwargs: A dict of keyword arguments to pass to `pd.read_csv()`, which is used to read in `filepath`

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
    loan_{balances, payments}: A nested list of dimensions [loans X n_payments] containing that loan's {balance,
        payment} history
    df: A pandas DataFrame of the payment and balance history for each loan, including the "total" payments and
    balances. Each row represents one payment from one loan.
    """

    def __init__(self, Loans: List[Loan]=None, payment: float = 0, filepath: str=None, principal_col: str='principal',
                 rate_col: str='rate', payment_col: str='payment', load_kwargs: dict=None):

        # Gather inputs
        assert bool(Loans) ^ bool(filepath), 'One, and only one, of `Loans` or `filepath` can be provided.'

        if filepath:
            self.filepath = filepath
            self.principal_col = principal_col
            self.rate_col = rate_col
            self.payment_col = payment_col
            if not load_kwargs:
                load_kwargs = {}
            self.load_kwargs = load_kwargs
            # Make loan objects
            Loans = self._load_file()
        else:
            for loan in Loans:
                if not isinstance(loan, Loan):
                    raise TypeError('`Loans` must be a list of `Loan` objects')

        # Initialize
        self.Loans = Loans
        self.payment = payment
        self.n_loans = len(Loans)
        self.reset()

        # Order loans by rate from highest to lowest
        rates = [loan.rate for loan in Loans]
        self._rate_order = np.argsort(rates)[::-1]

    def _load_file(self):
        """Load loan data from pd.read_csv() readable file"""
        # Load file
        loan_data = pd.read_csv(self.filepath, **self.load_kwargs)
        #
        # # Convert all to floats by removing strings
        # columns = [self.principal_col, self.rate_col, self.payment_col]
        #
        # loan_data = loan_data[columns].astype(str).applymap(lambda x: ''.join(re.findall('\d|/.', x))).astype(float)

        # Extract data
        principals = loan_data[self.principal_col]
        rates = loan_data[self.rate_col]
        payments = loan_data[self.payment_col]

        # Make loan objects
        loans = [Loan(p, r, pay) for p, r, pay in zip(principals, rates, payments)]
        return loans

    def pay_one(self, amount=None):
        """
        Apply a single payment period to all loans using Multiloan.payment as default amount
        amount: provide a recurring payment amount to override default
        """
        curr_payments = {i: 0 for i in range(len(self.Loans))}

        # First gather cost of a single payment
        for i, loan in enumerate(self.Loans):
            # Do a single payment to get payment amount
            # If balance is less than payment, balance will be returned
            min_pay = payment_amount(loan.payment, loan.balance)
            curr_payments[i] += min_pay

        # Balance after paying off minimum payments
        curr_min_payments = sum(curr_payments.values())

        # Now apply remainder of recurring amount
        if amount:
            recur_amount = amount
        else:
            recur_amount = self.payment
        curr_remaining = recur_amount - curr_min_payments
        assert curr_remaining >= 0, f'Multiloan payment ({money_amount(recur_amount)}) must exceed the sum of recurring payments for each Loan ({money_amount(curr_min_payments)})'

        # With remaining amount, now contribute to each loan in order of rate
        for idx in self._rate_order:
            if curr_remaining > 0:
                loan = self.Loans[idx]
                # Recalculate the single payment with the current remaining for each loan + what has already been paid
                curr_min = curr_payments[idx]
                _, residual_payment = single_payment(curr_remaining + curr_min, loan.balance, loan.rate, loan.n, loan.t)
                # Update loan payment
                curr_payments[idx] = residual_payment
                # Recalculate curr_remaining
                curr_remaining -= (residual_payment - curr_min)
            else:
                break

        # Now make loan contributions
        for idx, payment in curr_payments.items():
            loan = self.Loans[idx]
            # Make payment
            loan.pay_one(payment)

        # Now update data
        curr_total_payment = sum(curr_payments.values())
        self._payments.append(curr_total_payment)
        curr_balance = sum([loan.balance for loan in self.Loans])
        self._balances.append(curr_balance)

    def pay_remaining(self, amount=None):
        """
        Pay off the remaining balance to all loans using Multiloan.payment as default recurring payment amount
        amount: provide a recurring payment amount to override default
        """
        while self.balance > 0:
            self.pay_one(amount)


    def reset(self):
        """
        Reset payment loan payment history
        """
        self._payments = [0]
        self.principal = sum([loan.principal for loan in self.Loans])
        self._balances = [self.principal]
        for loan in self.Loans:
            loan.reset()

    @property
    def balance(self):
        return self._balances[-1]

    @property
    def totalpay(self):
        return sum(self._payments)

    @property
    def n_payments(self):
        return len(self._payments) - 1

    @property
    def loan_balances(self):
        """Get list of balances after each payment for each loan"""
        return np.array([loan._balances for loan in self.Loans])

    @property
    def loan_payments(self):
        """Get list of payments for each loan"""
        return np.array([loan._payments for loan in self.Loans])

    @property
    def payments(self):
        return np.array(self._payments)

    @property
    def balances(self):
        return np.array(self._balances)

    @property
    def df(self):
        """DataFrame of payment history for each loan including 'total'"""
        # Get data for each loan
        data = [{'loan': 'loan_%s' % i, 'amount': p, 'balance': b, 'payment': n}
                for i, loan in enumerate(self.Loans)
                for p, b, n in zip(loan._payments, loan._balances, range(self.n_payments))]
        # Get data for total
        total_data = [{'loan': 'total', 'amount': p, 'balance': b, 'payment': n} for p, b, n
                      in zip(self._payments, self._balances, range(self.n_payments))]
        # Combine into one list
        data += total_data
        # DataFrame
        df = pd.DataFrame(data)
        return df



    def __repr__(self):
        rep = f'Multiloan(loans={self.n_loans}, original={money_amount(self.principal)}, ' \
              f'balance={money_amount(self.balance)})'
        return rep

    def __str__(self):
        rep = f"""\
Number of loans: {self.n_loans}
Original principal: {money_amount(self.principal)}
Current balance: {money_amount(self.balance)}
Payment amount: {money_amount(self.payment)}
Total amount paid: {money_amount(self.totalpay)}
Number of payments: {self.n_payments}"""
        return rep


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

    def __init__(self, loan: Union[Loan, MultiLoan], payrange: list):
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
        pct_changes = np.append(np.diff(totals), 0) / totals

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
