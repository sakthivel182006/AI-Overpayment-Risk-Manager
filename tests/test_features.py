import os
import sys
import unittest

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "src")
    )
)

from feature_engineering import create_features


class TestFeatureEngineering(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.df = create_features()

    def test_features_created(self):
        self.assertGreater(len(self.df), 0)

    def test_expected_features_exist(self):

        expected_features = [
            "average_payment_to_award_ratio",
            "maximum_payment_to_award_ratio",
            "payment_variability",
            "adjustment_rate",
            "needs_figure",
            "award_to_needs_ratio",
            "unusual_payment_count",
            "first_month_payment",
            "last_month_payment",
            "first_to_last_change",
            "first_to_last_change_pct",
            "high_payment_months",
            "months_above_award",
            "largest_monthly_increase",
            "largest_monthly_decrease"
        ]

        for feature in expected_features:
            self.assertIn(
                feature,
                self.df.columns
            )

    def test_no_missing_feature_values(self):

        feature_columns = [
            "average_payment_to_award_ratio",
            "maximum_payment_to_award_ratio",
            "payment_variability",
            "adjustment_rate",
            "award_to_needs_ratio",
            "high_payment_months",
            "months_above_award"
        ]

        for column in feature_columns:
            self.assertFalse(
                self.df[column].isna().any()
            )

    def test_risk_ratios_are_non_negative(self):

        self.assertTrue(
            (
                self.df[
                    "average_payment_to_award_ratio"
                ] >= 0
            ).all()
        )

        self.assertTrue(
            (
                self.df[
                    "maximum_payment_to_award_ratio"
                ] >= 0
            ).all()
        )

    def test_high_payment_months_range(self):

        self.assertTrue(
            self.df[
                "high_payment_months"
            ].between(0, 6).all()
        )

    def test_months_above_award_range(self):

        self.assertTrue(
            self.df[
                "months_above_award"
            ].between(0, 6).all()
        )


if __name__ == "__main__":
    unittest.main()