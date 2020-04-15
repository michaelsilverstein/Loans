"""Test utility functions"""

from unittest import TestCase
from multiloan.utils import money_amount, pay_loan


class TestUtils(TestCase):
    def test_money_amount(self):
        """Test money amount string formatting"""
        inputs = [100, 100.123, 1000, 1e6]
        expected = ['$100.00', '$100.12', '$1,000.00', '$1,000,000.00']

        # Format inputs
        formatted = [money_amount(i) for i in inputs]

        # Check
        self.assertEqual(formatted, expected)

    def test_break_payloan(self):
        """Test that pay_loan() gives error with insufficient payment"""
        principal = 1e4
        rate = .05
        payment = 1
        stop = 1e6

        # Test break
        expected_message = f'Payments of {money_amount(payment)} have led the balance to reach stopping criteria of' \
                          f' {money_amount(stop)}.'

        with self.assertRaises(AssertionError) as error:
            pay_loan(payment, principal, rate)

        error_msg = str(error.exception)

        self.assertEqual(expected_message, error_msg)

        # Test that no error when there shouldn't be
        payment = 200
        try:
            pay_loan(payment, principal, rate)
        except AssertionError:
            self.fail()