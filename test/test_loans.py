"""Test loan classes"""

from unittest import TestCase
from multiloan.loans import Loan

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
        # Check that total pay and payments are zero
        for attr in ['totalpay', 'n_payments']:
            self.assertEqual(getattr(loan, attr), 0)

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


