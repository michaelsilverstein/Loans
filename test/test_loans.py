"""Test loan classes"""

from unittest import TestCase
from multiloan.loans import Loan, MultiLoan, Payrange
import os
from warnings import simplefilter


class TestLoan(TestCase):
    def setUp(self):
        self.principal = 1e4
        self.rate = .05
        self.payment = 200
        self.loan = Loan(self.principal, self.rate, self.payment)

    def test_payremaining(self):
        """Test that balance is zero after paying off"""
        loan = self.loan
        loan.pay_remaining()
        self.assertEqual(loan.balance, 0)

    def test_reset(self):
        """Test resetting loan"""
        loan = self.loan
        # Pay off
        loan.pay_remaining()
        # Reset
        loan.reset()
        # Check that loan data hasn't changed
        for attr in ['principal', 'rate', 'payment']:
            self.assertEqual(getattr(loan, attr), getattr(self, attr))
        # Check that balance is principal
        self.assertEqual(loan.balance, self.principal)

    def test_payone_and_remaining(self):
        """Test that balance after paying once is the same as first payment in full pay off"""
        loan = self.loan
        # Get amount of one payment
        loan.pay_one()
        one_pay_balance = loan.balance

        # Get balance after first payment after paying off entirely
        loan.reset()
        loan.pay_remaining()
        all_pay_balance = loan._balances[1]

        self.assertEqual(one_pay_balance, all_pay_balance)

    def test_all_positive(self):
        """Test that all payments and balances are positive"""
        loan = self.loan

        loan.pay_remaining()

        self.assertTrue(list(loan.balances > 0))

        self.assertTrue(list(loan.payments > 0))

class TestMultiloan(TestCase):
    def setUp(self):
        # Create some loans
        principals = [1e3, 1e4, 1e5]
        rates = [.03, .04, .05]
        payments = [200, 300, 400]

        loans = [Loan(p, r, pay) for p, r, pay in zip(principals, rates, payments)]

        # Create a multiloan
        ml = MultiLoan(loans, 100000)

        self.prinicipals = principals
        self.loans = loans
        self.multiloan = ml

    def test_ml_balance(self):
        """Multiloan starting balance should equal the sum of loan principals"""
        ml_balance = self.multiloan.balance
        ml_principal = self.multiloan.principal
        ml_loan_principals = sum([loan.principal for loan in self.multiloan.Loans])
        principal_sums = sum(self.prinicipals)

        self.assertTrue(ml_balance == ml_principal == ml_loan_principals == principal_sums)

    def test_fail_multiple_inputs(self):
        """Only a list of loans or a file should be allowed to be provided"""
        # Try to load a list of loans and a file
        with self.assertRaises(AssertionError) as error:
            MultiLoan(self.loans, filepath='test_loan_table.csv')

        self.assertEqual(str(error.exception), 'One, and only one, of `Loans` or `filepath` can be provided.')

        with self.assertRaises(AssertionError) as error:
            MultiLoan()

        self.assertEqual(str(error.exception), 'One, and only one, of `Loans` or `filepath` can be provided.')

    def test_load_file(self):
        """Test that loading a file produces same results as using multiple loans"""
        self.multiloan.pay_remaining()
        balances_manual = self.multiloan._balances
        filepath = os.path.join(os.path.dirname(__file__) , 'test_loan_table.csv')
        new_ml = MultiLoan(filepath=filepath, payment=100000)
        new_ml.pay_remaining()

        balances_file = new_ml._balances

        self.assertEqual(balances_manual, balances_file)

    def test_fail_bad_loan_list(self):
        """If a list of loans provided, all must be Loan object"""
        bad_list = self.loans + ['test']

        with self.assertRaises(TypeError) as error:
            MultiLoan(bad_list)

        self.assertEqual(str(error.exception), '`Loans` must be a list of `Loan` objects')

    def test_fail_amount(self):
        """Fail a payment that is too small"""
        with self.assertRaises(AssertionError) as error:
            self.multiloan.pay_remaining(500)

        self.assertEqual(str(error.exception), 'Multiloan payment ($500.00) must exceed the sum of recurring '
                                               'payments for each Loan ($900.00)')

    def test_loan_history_equals_multi(self):
        """Sum of payments and balances of each loan should equal that of mulitloan"""

        # Pay off whole loan
        ml = self.multiloan
        ml.pay_remaining()

        # Check balances
        loan_balances_sum = list(ml.loan_balances.sum(0))
        ml_balances = ml._balances

        self.assertEqual(loan_balances_sum, ml_balances)

        # Check payments
        loan_payments_sum = list(ml.loan_payments.sum(0))
        ml_payments = ml._payments

        self.assertEqual(loan_payments_sum, ml_payments)

    def test_all_positive(self):
        """Test that all payments and balances are positive"""
        ml = self.multiloan

        ml.pay_remaining()

        self.assertTrue(list(ml.balances > 0))

        self.assertTrue(list(ml.payments > 0))

    def test_loan_totals(self):
        """Test that loan totals sum to multiloan total"""
        ml = self.multiloan
        ml.pay_remaining()

        self.assertTrue(round(ml.loan_totals.sum(), 2) == ml.totalpay == ml.payments.sum())

class TestPayRange(TestCase):
    def setUp(self):
        # Create a multiloan
        filepath = os.path.join(os.path.dirname(__file__), 'test_loan_table.csv')
        ml = MultiLoan(filepath=filepath, payment=10000)
        self.multiloan = ml

        # Create a payrange
        self.pr_multi = Payrange(ml, range(900, 1200, 50))

    def test_loan_totals_payments(self):
        """Test that the extracted loan_totals == loan_payments"""
        pr = self.pr_multi

        loan_totals = pr.loan_totals
        sum_loan_payments = pr.loan_amounts.sum(2)

        for lt, slp in zip(loan_totals, sum_loan_payments):
            rounded_lt = [round(i, 2) for i in lt]
            rounded_slp = [round(i, 2) for i in slp]
            self.assertEqual(rounded_lt, rounded_slp)

    def test_totals_loan_totals(self):
        """Sum of loan totals should equal totals"""
        pr = self.pr_multi

        totals = [round(i, 2) for i in pr.totals]
        sum_loan_totals = [round(i, 2) for i in pr.loan_totals.sum(1)]

        self.assertEqual(totals, sum_loan_totals)

    def test_pr_fail(self):
        """Payrange should fail if none of the amounts are sufficient"""
        with self.assertRaises(AssertionError) as error:
            simplefilter('ignore')
            Payrange(self.multiloan, [100])

        self.assertEqual(str(error.exception), 'No payment amount in the provided payrange is sufficient')

    def test_warning(self):
        """Test that a warning is raised if too low of payments are provided"""

        with self.assertWarns(UserWarning) as w:
            Payrange(self.multiloan, [100, 1000])

        self.assertEqual(str(w.warning), 'A payment amount was skipped because it surpassed stop criteria')

