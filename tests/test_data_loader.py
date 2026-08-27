import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from data_loader import load_data


class TestDataLoader(unittest.TestCase):

    def test_load_data(self):
        cases, payments = load_data()

        self.assertIsNotNone(cases)
        self.assertIsNotNone(payments)

    def test_cases_not_empty(self):
        cases, _ = load_data()

        self.assertGreater(len(cases), 0)

    def test_payments_not_empty(self):
        _, payments = load_data()

        self.assertGreater(len(payments), 0)

    def test_case_id_exists(self):
        cases, _ = load_data()

        self.assertIn("case_id", cases.columns)

    def test_payment_case_id_exists(self):
        _, payments = load_data()

        self.assertIn("case_id", payments.columns)


if __name__ == "__main__":
    unittest.main()