import os
import pandas as pd

from feature_engineering import create_features
from risk_scoring import calculate_risk_score
from investigator_feedback import apply_investigator_feedback


TOP_N = 20


def generate_explanation(row):
    """
    Generate a plain-language explanation based on
    payment evidence and investigator feedback.
    """

    reasons = []

    # ==========================================
    # 1. Average payment vs award
    # ==========================================

    average_ratio = row["average_payment_to_award_ratio"]

    if average_ratio >= 2:
        reasons.append(
            f"the average payment was {average_ratio:.1f} times "
            f"the recorded monthly award"
        )

    elif average_ratio >= 1.25:
        reasons.append(
            f"the average payment was {average_ratio:.1f} times "
            f"the recorded monthly award"
        )

    # ==========================================
    # 2. Maximum payment vs award
    # ==========================================

    maximum_ratio = row["maximum_payment_to_award_ratio"]

    if maximum_ratio >= 2:
        reasons.append(
            f"the largest payment was {maximum_ratio:.1f} times "
            f"the recorded monthly award"
        )

    elif maximum_ratio >= 1.5:
        reasons.append(
            f"the largest payment was {maximum_ratio:.1f} times "
            f"the recorded monthly award"
        )

    # ==========================================
    # 3. Persistent high-payment pattern
    # ==========================================

    high_months = int(row["high_payment_months"])

    if high_months == 6:
        reasons.append(
            "payments exceeded 1.5 times the recorded monthly "
            "award in all six months"
        )

    elif high_months >= 3:
        reasons.append(
            f"payments exceeded 1.5 times the recorded monthly "
            f"award in {high_months} of six months"
        )

    elif high_months > 0:
        reasons.append(
            f"payments exceeded 1.5 times the recorded monthly "
            f"award in {high_months} month(s)"
        )

    # ==========================================
    # 4. Months above award
    # ==========================================

    months_above = int(row["months_above_award"])

    if months_above == 6:
        reasons.append(
            "payments were above the recorded award in every month"
        )

    elif months_above >= 4:
        reasons.append(
            f"payments were above the recorded award in "
            f"{months_above} of six months"
        )

    # ==========================================
    # 5. Payment variability
    # ==========================================

    variability = row["payment_variability"]

    if variability >= 0.15:
        reasons.append(
            "monthly payment amounts showed substantial variation"
        )

    elif variability >= 0.10:
        reasons.append(
            "monthly payment amounts showed noticeable variation"
        )

    # ==========================================
    # 6. Sudden monthly increase
    # ==========================================

    largest_increase = row["largest_monthly_increase"]

    if largest_increase >= 500:
        reasons.append(
            f"one monthly payment increase was "
            f"${largest_increase:,.2f}"
        )

    # ==========================================
    # 7. Main explanation
    # ==========================================

    if not reasons:
        main_explanation = (
            "the payment pattern was unusual compared "
            "with the wider case population"
        )

    elif len(reasons) == 1:
        main_explanation = reasons[0]

    elif len(reasons) == 2:
        main_explanation = (
            reasons[0] + " and " + reasons[1]
        )

    else:
        main_explanation = (
            ", ".join(reasons[:-1]) +
            ", and " +
            reasons[-1]
        )

    explanation = (
        "High review priority because "
        + main_explanation
        + "."
    )

    # ==========================================
    # 8. Investigator-context warning
    # ==========================================

    if row["administrative_activity_flag"] == 1:

        explanation += (
            " Note: this case also has administrative activity "
            f"({row['administrative_context']}), which may have "
            "a legitimate explanation and should not itself be "
            "treated as evidence of improper payment."
        )

    # ==========================================
    # 9. Human-review boundary
    # ==========================================

    explanation += (
        " This is a review signal, not a finding of improper payment."
    )

    return explanation


def create_explanations():

    print("\n========================================")
    print("FINAL INVESTIGATOR WORKLIST")
    print("========================================")

    # ==========================================
    # Step 1: Create features
    # ==========================================

    df = create_features()

    # ==========================================
    # Step 2: Calculate existing risk score
    # ==========================================

    df = calculate_risk_score(df)

    # ==========================================
    # Step 3: Incorporate investigator feedback
    # ==========================================

    df = apply_investigator_feedback(df)

    # ==========================================
    # Step 4: Rank cases
    # ==========================================

    df = df.sort_values(
        by="final_risk_score",
        ascending=False
    ).reset_index(drop=True)

    # ==========================================
    # Step 5: Select TOP 20
    # ==========================================

    top20 = df.head(TOP_N).copy()

    top20["rank"] = range(1, TOP_N + 1)

    # ==========================================
    # Step 6: Generate explanations
    # ==========================================

    top20["explanation"] = top20.apply(
        generate_explanation,
        axis=1
    )

    # ==========================================
    # Step 7: Create final output
    # ==========================================

    output = top20[
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

    # Rename final score for cleaner output
    output = output.rename(
        columns={
            "final_risk_score": "risk_score"
        }
    )

    # ==========================================
    # Step 8: Save final TOP 20
    # ==========================================

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output.to_csv(
        "outputs/top20_cases.csv",
        index=False
    )

    # ==========================================
    # Step 9: Display worklist
    # ==========================================

    for _, row in output.iterrows():

        print(
            f"\n#{int(row['rank'])} "
            f"{row['case_id']} "
            f"(Risk Score: {row['risk_score']:.2f})"
        )

        print(
            f"Reason: {row['explanation']}"
        )

    # ==========================================
    # Complete
    # ==========================================

    print("\n========================================")
    print("FINAL TOP 20 SAVED")
    print("========================================")

    print(
        "outputs/top20_cases.csv"
    )

    return output


if __name__ == "__main__":
    create_explanations()