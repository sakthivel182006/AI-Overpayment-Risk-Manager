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
from investigator_feedback import apply_investigator_feedback
from ranking import rank_cases


class TestRanking(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        features = create_features()

        scored = calculate_risk_score(
            features
        )

        feedback = apply_investigator_feedback(
            scored
        )

        cls.ranked, cls.top20 = rank_cases(
            feedback,
            20
        )

    def test_all_cases_are_ranked(self):

        self.assertEqual(
            len(self.ranked),
            4200
        )

    def test_top20_has_20_cases(self):

        self.assertEqual(
            len(self.top20),
            20
        )

    def test_rank_column_exists(self):

        self.assertIn(
            "rank",
            self.ranked.columns
        )

    def test_ranking_is_descending(self):

        scores = self.ranked[
            "final_risk_score"
        ].tolist()

        self.assertEqual(
            scores,
            sorted(
                scores,
                reverse=True
            )
        )

    def test_top_rank_is_one(self):

        self.assertEqual(
            self.top20.iloc[0]["rank"],
            1
        )

    def test_top20_ranks(self):

        expected_ranks = list(
            range(1, 21)
        )

        actual_ranks = (
            self.top20["rank"]
            .tolist()
        )

        self.assertEqual(
            actual_ranks,
            expected_ranks
        )

    def test_top_score_is_highest(self):

        top_score = self.top20.iloc[0][
            "final_risk_score"
        ]

        maximum_score = self.ranked.iloc[0][
            "final_risk_score"
        ]

        self.assertEqual(
            top_score,
            maximum_score
        )


if __name__ == "__main__":
    unittest.main()