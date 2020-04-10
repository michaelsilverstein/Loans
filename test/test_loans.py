"""Test loan classes"""

from unittest import TestCase
from multiloan.loans import Loan, MultiLoan

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
        all_pay_balance = loan.balances[1]

        self.assertEqual(one_pay_balance, all_pay_balance)

class TestMultiloan(TestCase):
    def setUp(self):
        # Create some loans
        principals = [1e3, 1e4, 1e5]
        rates = [.03, .04, .05]
        payments = [200, 300, 400]

        loans = [Loan(p, r, pay) for p, r, pay in zip(principals, rates, payments)]

        # Create a multiloan
        ml = MultiLoan(loans, 500)

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
    def test_fail_bad_loan_list(self):
        """If a list of loans provided, all must be Loan object"""
        bad_list = self.loans + ['test']

        with self.assertRaises(TypeError) as error:
            MultiLoan(bad_list)

        self.assertEqual(str(error.exception), '`Loans` must be a list of `Loan` objects')