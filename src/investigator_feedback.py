import pandas as pd

from feature_engineering import create_features
from risk_scoring import calculate_risk_score


# Investigator-reviewed case from Day 2 feedback
REVIEWED_CASE_ID = "C-33248"


def identify_administrative_risk(df):
    """
    Identify cases where administrative activity may need
    additional investigator context.

    Important:
    These signals are NOT treated as evidence of improper payment.
    They are only used to warn the investigator that the case
    may contain legitimate administrative activity.
    """

    df = df.copy()

    # Administrative activity indicators
    df["administrative_activity_flag"] = (
        (
            (df["payment_adjustments"] >= 4)
            |
            (df["contact_attempts"] >= 6)
        )
    ).astype(int)

    # Explain why the flag exists
    def get_context(row):

        reasons = []

        if row["payment_adjustments"] >= 4:
            reasons.append(
                f"{int(row['payment_adjustments'])} payment adjustments"
            )

        if row["contact_attempts"] >= 6:
            reasons.append(
                f"{int(row['contact_attempts'])} contact attempts"
            )

        if reasons:
            return " and ".join(reasons)

        return ""

    df["administrative_context"] = df.apply(
        get_context,
        axis=1
    )

    return df


def apply_investigator_feedback(df):
    """
    Incorporate the Day 2 investigator lesson.

    We DO NOT remove cases simply because they have
    administrative activity.

    Instead, we preserve the payment-risk score and add
    contextual information for investigator review.
    """

    df = identify_administrative_risk(df)

    # -------------------------------------------------
    # Important governance rule
    # -------------------------------------------------
    #
    # Administrative activity must NOT automatically
    # increase the risk score.
    #
    # This prevents:
    #
    # adjustments + contact attempts
    #            ↓
    #     automatic suspicion
    #
    # The original payment-risk score remains unchanged.
    # -------------------------------------------------

    df["final_risk_score"] = df["risk_score"]

    # Add investigator context
    df["investigator_context"] = df.apply(
        lambda row: (
            "Administrative activity may have a legitimate "
            "explanation and should not be treated as evidence "
            "of improper payment."
            if row["administrative_activity_flag"] == 1
            else
            "No strong administrative-activity warning detected."
        ),
        axis=1
    )

    return df


def run_investigator_feedback():

    print("\n========================================")
    print("INVESTIGATOR FEEDBACK")
    print("========================================")

    # -------------------------------------------------
    # Load existing feature pipeline
    # -------------------------------------------------

    df = create_features()

    # -------------------------------------------------
    # Calculate existing risk score
    # -------------------------------------------------

    df = calculate_risk_score(df)

    # -------------------------------------------------
    # Apply Day 2 feedback
    # -------------------------------------------------

    df = apply_investigator_feedback(df)

    # -------------------------------------------------
    # Rank using the original risk score
    # -------------------------------------------------

    df = df.sort_values(
        by="final_risk_score",
        ascending=False
    ).reset_index(drop=True)

    # -------------------------------------------------
    # Display reviewed case if it exists
    # -------------------------------------------------

    reviewed_case = df[
        df["case_id"] == REVIEWED_CASE_ID
    ]

    print("\nDay 2 investigator-reviewed case:")

    if len(reviewed_case) > 0:

        row = reviewed_case.iloc[0]

        print(
            f"\nCase: {row['case_id']}"
        )

        print(
            f"Risk score: {row['risk_score']:.2f}"
        )

        print(
            f"Payment adjustments: "
            f"{int(row['payment_adjustments'])}"
        )

        print(
            f"Contact attempts: "
            f"{int(row['contact_attempts'])}"
        )

        print(
            f"Administrative context: "
            f"{row['administrative_context']}"
        )

        print(
            f"Investigator warning: "
            f"{row['investigator_context']}"
        )

    else:

        print(
            f"{REVIEWED_CASE_ID} was not found."
        )

    # -------------------------------------------------
    # Show cases with administrative context
    # -------------------------------------------------

    print("\n========================================")
    print("ADMINISTRATIVE CONTEXT CHECK")
    print("========================================")

    context_cases = df[
        df["administrative_activity_flag"] == 1
    ].copy()

    print(
        f"\nCases with administrative context: "
        f"{len(context_cases)}"
    )

    print("\nExamples:")

    print(
        context_cases[
            [
                "case_id",
                "risk_score",
                "payment_adjustments",
                "contact_attempts",
                "administrative_context"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    # -------------------------------------------------
    # Save output
    # -------------------------------------------------

    import os

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    output_columns = [
        "case_id",
        "risk_score",
        "final_risk_score",
        "payment_adjustments",
        "contact_attempts",
        "administrative_activity_flag",
        "administrative_context",
        "investigator_context"
    ]

    df[output_columns].to_csv(
        "outputs/investigator_feedback_analysis.csv",
        index=False
    )

    print("\n========================================")
    print("FEEDBACK ANALYSIS COMPLETE")
    print("========================================")

    print(
        "\nSaved to:"
    )

    print(
        "outputs/investigator_feedback_analysis.csv"
    )

    return df


if __name__ == "__main__":
    run_investigator_feedback()