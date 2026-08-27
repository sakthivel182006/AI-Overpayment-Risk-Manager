import os
import pandas as pd

from feature_engineering import create_features
from risk_scoring import calculate_risk_score
from investigator_feedback import apply_investigator_feedback


TOP_N = 20


def rank_cases(df, top_n=TOP_N):
    """
    Rank all cases by their final risk score
    and return the highest-priority cases.
    """

    df = df.copy()

    # Sort highest risk first
    ranked_df = df.sort_values(
        by="final_risk_score",
        ascending=False
    ).reset_index(drop=True)

    # Add investigator rank
    ranked_df["rank"] = (
        ranked_df.index + 1
    )

    # Select TOP N
    top_cases = ranked_df.head(top_n).copy()

    return ranked_df, top_cases


def create_ranking():

    print("\n========================================")
    print("CASE RANKING")
    print("========================================")

    # ==========================================
    # 1. Create features
    # ==========================================

    df = create_features()

    print(
        f"\nTotal cases available: {len(df)}"
    )

    # ==========================================
    # 2. Calculate risk scores
    # ==========================================

    df = calculate_risk_score(df)

    # ==========================================
    # 3. Apply investigator feedback
    # ==========================================

    df = apply_investigator_feedback(df)

    # ==========================================
    # 4. Rank cases
    # ==========================================

    ranked_df, top20 = rank_cases(df)

    # ==========================================
    # 5. Save complete ranking
    # ==========================================

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    ranked_df.to_csv(
        "outputs/all_ranked_cases.csv",
        index=False
    )

    # ==========================================
    # 6. Save TOP 20
    # ==========================================

    top20_output = top20[
        [
            "rank",
            "case_id",
            "final_risk_score",
            "average_payment_to_award_ratio",
            "maximum_payment_to_award_ratio",
            "high_payment_months",
            "months_above_award",
            "payment_variability",
            "administrative_activity_flag"
        ]
    ].copy()

    top20_output = top20_output.rename(
        columns={
            "final_risk_score": "risk_score"
        }
    )

    top20_output.to_csv(
        "outputs/top20_cases.csv",
        index=False
    )

    # ==========================================
    # 7. Display TOP 20
    # ==========================================

    print("\n========================================")
    print("TOP 20 CASES")
    print("========================================")

    print(
        top20_output.to_string(
            index=False
        )
    )

    # ==========================================
    # 8. Summary
    # ==========================================

    print("\n========================================")
    print("RANKING COMPLETE")
    print("========================================")

    print(
        "\nComplete ranking:"
    )

    print(
        "outputs/all_ranked_cases.csv"
    )

    print(
        "\nTOP 20 worklist:"
    )

    print(
        "outputs/top20_cases.csv"
    )

    return ranked_df, top20


if __name__ == "__main__":
    create_ranking()