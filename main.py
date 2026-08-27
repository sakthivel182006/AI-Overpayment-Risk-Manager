import os
import sys

# Add src directory to Python path
SRC_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "src"
)

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)


from feature_engineering import create_features
from risk_scoring import calculate_risk_score
from investigator_feedback import apply_investigator_feedback
from ranking import rank_cases
from explanations import generate_explanation
from fairness import calculate_fairness


TOP_N = 20


def run_complete_pipeline():

    print("\n")
    print("=" * 60)
    print("AI OVERPAYMENT RISK MANAGER")
    print("COMPLETE PIPELINE")
    print("=" * 60)

    # =========================================================
    # STEP 1 — Feature Engineering
    # =========================================================

    print("\n[1/5] Creating features...")

    df = create_features()

    print(
        f"Cases processed: {len(df)}"
    )

    print(
        f"Features generated: {len(df.columns)}"
    )

    # =========================================================
    # STEP 2 — Risk Scoring
    # =========================================================

    print("\n[2/5] Calculating risk scores...")

    df = calculate_risk_score(df)

    print("Risk scores calculated successfully.")

    # =========================================================
    # STEP 3 — Investigator Feedback
    # =========================================================

    print("\n[3/5] Applying investigator feedback...")

    df = apply_investigator_feedback(df)

    print(
        "Administrative activity is treated as "
        "investigator context, not automatic risk evidence."
    )

    # =========================================================
    # STEP 4 — Ranking
    # =========================================================

    print("\n[4/5] Ranking cases...")

    ranked_df, top20 = rank_cases(
        df,
        TOP_N
    )

    # Save complete ranking
    os.makedirs(
        "outputs",
        exist_ok=True
    )

    ranked_df.to_csv(
        "outputs/all_ranked_cases.csv",
        index=False
    )

    # =========================================================
    # Generate TOP 20 explanations
    # =========================================================

    top20 = top20.copy()

    top20["explanation"] = top20.apply(
        generate_explanation,
        axis=1
    )

    top20["rank"] = range(
        1,
        len(top20) + 1
    )

    final_top20 = top20[
        [
            "rank",
            "case_id",
            "final_risk_score",
            "average_payment",
            "monthly_award",
            "maximum_payment",
            "high_payment_months",
            "months_above_award",
            "payment_variability",
            "administrative_activity_flag",
            "administrative_context",
            "explanation"
        ]
    ].copy()

    final_top20 = final_top20.rename(
        columns={
            "final_risk_score": "risk_score"
        }
    )

    final_top20.to_csv(
        "outputs/top20_cases.csv",
        index=False
    )

    # =========================================================
    # Display TOP 20
    # =========================================================

    print("\n" + "=" * 60)
    print("TOP 20 INVESTIGATOR WORKLIST")
    print("=" * 60)

    for _, row in final_top20.iterrows():

        print(
            f"\n#{int(row['rank'])} "
            f"{row['case_id']} "
            f"| Risk Score: {row['risk_score']:.2f}"
        )

        print(
            f"Reason: {row['explanation']}"
        )

    # =========================================================
    # STEP 5 — Fairness Analysis
    # =========================================================

    print("\n[5/5] Running fairness analysis...")

    # Mark TOP 20
    df["review_priority"] = 0

    top_case_ids = set(
        top20["case_id"]
    )

    df.loc[
        df["case_id"].isin(top_case_ids),
        "review_priority"
    ] = 1

    demographic_fields = [
        "age_band",
        "language_preference",
        "district",
        "tenure"
    ]

    fairness_results = []

    for column in demographic_fields:

        result = calculate_fairness(
            df,
            column
        )

        result.insert(
            0,
            "dimension",
            column
        )

        fairness_results.append(
            result
        )

    fairness_report = __import__(
        "pandas"
    ).concat(
        fairness_results,
        ignore_index=True
    )

    fairness_report.to_csv(
        "outputs/fairness_report.csv",
        index=False
    )

    # =========================================================
    # Final Summary
    # =========================================================

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    print(
        f"\nTotal cases analysed : {len(df)}"
    )

    print(
        f"TOP cases selected   : {len(final_top20)}"
    )

    print(
        "\nGenerated files:"
    )

    print(
        "  ✓ outputs/all_ranked_cases.csv"
    )

    print(
        "  ✓ outputs/top20_cases.csv"
    )

    print(
        "  ✓ outputs/fairness_report.csv"
    )

    print("\n" + "=" * 60)
    print("READY FOR INVESTIGATOR REVIEW")
    print("=" * 60)


if __name__ == "__main__":
    run_complete_pipeline()