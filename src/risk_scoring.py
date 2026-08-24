import pandas as pd

from feature_engineering import create_features


def calculate_risk_score(df):
    """
    Calculate an explainable risk score for every case.

    The score is based mainly on payment behaviour:
    - Average payment compared with award
    - Maximum payment compared with award
    - Number of high-payment months
    - Number of months above the award
    - Payment variability
    - Sudden monthly payment increases

    Administrative activity such as contact attempts is NOT used
    as a risk signal because investigator feedback showed that it
    can have legitimate explanations.
    """

    # Make a copy so the original dataframe is not changed
    df = df.copy()

    # =========================================================
    # 1. Average payment vs award
    # =========================================================

    average_ratio_score = (
        (df["average_payment_to_award_ratio"] - 1)
        .clip(lower=0)
        / 1.5
        * 25
    ).clip(upper=25)

    # =========================================================
    # 2. Maximum payment vs award
    # =========================================================

    maximum_ratio_score = (
        (df["maximum_payment_to_award_ratio"] - 1)
        .clip(lower=0)
        / 2
        * 20
    ).clip(upper=20)

    # =========================================================
    # 3. Persistent high-payment months
    # =========================================================

    high_month_score = (
        df["high_payment_months"] / 6 * 25
    ).clip(upper=25)

    # =========================================================
    # 4. Months above award
    # =========================================================

    above_award_score = (
        df["months_above_award"] / 6 * 15
    ).clip(upper=15)

    # =========================================================
    # 5. Payment variability
    # =========================================================

    variability_score = (
        df["payment_variability"] / 0.25 * 10
    ).clip(upper=10)

    # =========================================================
    # 6. Final risk score
    # =========================================================

    df["risk_score"] = (
        average_ratio_score
        + maximum_ratio_score
        + high_month_score
        + above_award_score
        + variability_score
    )

    # Make sure score stays between 0 and 100
    df["risk_score"] = (
        df["risk_score"]
        .clip(0, 100)
        .round(2)
    )

    # =========================================================
    # 7. Store individual signal scores
    # =========================================================

    df["average_ratio_score"] = (
        average_ratio_score.round(2)
    )

    df["maximum_ratio_score"] = (
        maximum_ratio_score.round(2)
    )

    df["high_month_score"] = (
        high_month_score.round(2)
    )

    df["above_award_score"] = (
        above_award_score.round(2)
    )

    df["variability_score"] = (
        variability_score.round(2)
    )

    return df


if __name__ == "__main__":

    print("\n========================================")
    print("RISK SCORING")
    print("========================================")

    # Create features
    df = create_features()

    # Calculate risk scores
    df = calculate_risk_score(df)

    # Sort highest risk first
    ranked = df.sort_values(
        by="risk_score",
        ascending=False
    )

    # =========================================================
    # Display TOP 20
    # =========================================================

    print("\nTOP 20 CASES")
    print("----------------------------------------")

    top20_columns = [
        "case_id",
        "risk_score",
        "average_payment_to_award_ratio",
        "maximum_payment_to_award_ratio",
        "high_payment_months",
        "months_above_award",
        "payment_variability"
    ]

    print(
        ranked[top20_columns]
        .head(20)
        .to_string(index=False)
    )

    # =========================================================
    # Display strongest signals
    # =========================================================

    print("\n========================================")
    print("RISK SCORE STATISTICS")
    print("========================================")

    print(
        ranked["risk_score"].describe()
    )

    print("\n========================================")
    print("RISK SCORING COMPLETE")
    print("========================================")