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
from risk_scoring import calculate_risk_score


class TestRiskScoring(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        features = create_features()

        cls.df = calculate_risk_score(
            features
        )

    def test_risk_score_exists(self):

        self.assertIn(
            "risk_score",
            self.df.columns
        )

    def test_risk_scores_are_not_missing(self):

        self.assertFalse(
            self.df["risk_score"].isna().any()
        )

    def test_risk_score_range(self):

        self.assertTrue(
            (
                self.df["risk_score"] >= 0
            ).all()
        )

        self.assertTrue(
            (
                self.df["risk_score"] <= 100
            ).all()
        )

    def test_score_components_exist(self):

        components = [
            "average_ratio_score",
            "maximum_ratio_score",
            "high_month_score",
            "above_award_score",
            "variability_score"
        ]

        for component in components:

            self.assertIn(
                component,
                self.df.columns
            )

    def test_score_is_numeric(self):

        self.assertTrue(
            self.df["risk_score"]
            .dtype.kind in "fi"
        )


if __name__ == "__main__":
    unittest.main()