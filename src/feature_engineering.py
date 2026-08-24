import pandas as pd


# Policy reference from the problem statement
NEEDS_FIGURE = {
    1: 1240,
    2: 1670,
    3: 2000,
    4: 2330,
    5: 2660,
    6: 2990
}


def create_features():

    # ==========================================
    # 1. Load data
    # ==========================================

    cases = pd.read_csv("data/cases.csv")
    payments = pd.read_csv("data/payments.csv")

    payments["pay_month"] = pd.to_datetime(payments["pay_month"])

    # ==========================================
    # 2. Basic payment features
    # ==========================================

    payment_summary = payments.groupby("case_id").agg(
        payment_count=("payment_id", "count"),
        total_paid=("amount", "sum"),
        average_payment=("amount", "mean"),
        maximum_payment=("amount", "max"),
        minimum_payment=("amount", "min"),
        payment_std=("amount", "std"),
        adjustment_payment_count=(
            "adjustment",
            lambda x: (x == "Y").sum()
        )
    ).reset_index()

    # ==========================================
    # 3. Merge cases + payments
    # ==========================================

    df = cases.merge(
        payment_summary,
        on="case_id",
        how="left"
    )

    # ==========================================
    # 4. Fill missing values
    # ==========================================

    numeric_columns = [
        "payment_count",
        "total_paid",
        "average_payment",
        "maximum_payment",
        "minimum_payment",
        "payment_std",
        "adjustment_payment_count"
    ]

    for column in numeric_columns:
        df[column] = df[column].fillna(0)

    # ==========================================
    # 5. Needs figure
    # ==========================================

    df["needs_figure"] = df["household_size"].map(NEEDS_FIGURE)

    # ==========================================
    # 6. Payment vs award features
    # ==========================================

    df["average_payment_to_award_ratio"] = (
        df["average_payment"] /
        df["monthly_award"]
    )

    df["maximum_payment_to_award_ratio"] = (
        df["maximum_payment"] /
        df["monthly_award"]
    )

    # ==========================================
    # 7. Payment variability
    # ==========================================

    df["payment_variability"] = (
        df["payment_std"] /
        df["average_payment"]
    )

    df["payment_variability"] = (
        df["payment_variability"]
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

    # ==========================================
    # 8. Adjustment rate
    # ==========================================

    df["adjustment_rate"] = (
        df["adjustment_payment_count"] /
        df["payment_count"]
    )

    df["adjustment_rate"] = (
        df["adjustment_rate"]
        .replace([float("inf"), -float("inf")], 0)
        .fillna(0)
    )

    # ==========================================
    # 9. Award vs needs
    # ==========================================

    df["award_to_needs_ratio"] = (
        df["monthly_award"] /
        df["needs_figure"]
    )

    # ==========================================
    # 10. Unusual payment count
    # ==========================================

    # Six months of payment data.
    # Six payments is the normal pattern.
    df["unusual_payment_count"] = (
        df["payment_count"] != 6
    ).astype(int)

    # ==========================================
    # 11. MONTHLY PAYMENT PATTERN FEATURES
    # ==========================================

    # Create monthly payment table
    monthly = payments.pivot_table(
        index="case_id",
        columns="pay_month",
        values="amount",
        aggfunc="sum"
    )

    # Sort months chronologically
    monthly = monthly.sort_index(axis=1)

    # Get month columns
    month_columns = list(monthly.columns)

    # ------------------------------------------
    # First payment and last payment
    # ------------------------------------------

    if len(month_columns) >= 2:

        df_monthly = monthly.reindex(df["case_id"])

        df["first_month_payment"] = (
            df_monthly[month_columns[0]].values
        )

        df["last_month_payment"] = (
            df_monthly[month_columns[-1]].values
        )

        # Change from first month to last month
        df["first_to_last_change"] = (
            df["last_month_payment"] -
            df["first_month_payment"]
        )

        # Percentage change
        df["first_to_last_change_pct"] = (
            df["first_to_last_change"] /
            df["first_month_payment"]
        )

        df["first_to_last_change_pct"] = (
            df["first_to_last_change_pct"]
            .replace([float("inf"), -float("inf")], 0)
            .fillna(0)
        )

    else:

        df["first_month_payment"] = 0
        df["last_month_payment"] = 0
        df["first_to_last_change"] = 0
        df["first_to_last_change_pct"] = 0

    # ------------------------------------------
    # Number of unusually high-payment months
    # ------------------------------------------

    # A month is considered high when payment
    # exceeds 1.5 times the recorded award.

    high_payment_counts = []

    for _, row in df.iterrows():

        case_id = row["case_id"]
        award = row["monthly_award"]

        if case_id in monthly.index:

            case_payments = monthly.loc[case_id]

            high_count = (
                case_payments >
                (award * 1.5)
            ).sum()

        else:
            high_count = 0

        high_payment_counts.append(high_count)

    df["high_payment_months"] = high_payment_counts

    # ------------------------------------------
    # Number of months above the award
    # ------------------------------------------

    above_award_counts = []

    for _, row in df.iterrows():

        case_id = row["case_id"]
        award = row["monthly_award"]

        if case_id in monthly.index:

            case_payments = monthly.loc[case_id]

            above_count = (
                case_payments > award
            ).sum()

        else:
            above_count = 0

        above_award_counts.append(above_count)

    df["months_above_award"] = above_award_counts

    # ------------------------------------------
    # Largest month-to-month increase
    # ------------------------------------------

    largest_increases = []

    for case_id in df["case_id"]:

        if case_id in monthly.index:

            values = monthly.loc[case_id].dropna()

            if len(values) >= 2:

                changes = values.diff()

                largest_increase = changes.max()

            else:
                largest_increase = 0

        else:
            largest_increase = 0

        largest_increases.append(largest_increase)

    df["largest_monthly_increase"] = largest_increases

    # ------------------------------------------
    # Largest month-to-month decrease
    # ------------------------------------------

    largest_decreases = []

    for case_id in df["case_id"]:

        if case_id in monthly.index:

            values = monthly.loc[case_id].dropna()

            if len(values) >= 2:

                changes = values.diff()

                largest_decrease = changes.min()

            else:
                largest_decrease = 0

        else:
            largest_decrease = 0

        largest_decreases.append(largest_decrease)

    df["largest_monthly_decrease"] = largest_decreases

    # ==========================================
    # 12. Final cleanup
    # ==========================================

    df = df.replace(
        [float("inf"), -float("inf")],
        0
    )

    df = df.fillna(0)

    return df


# ==============================================
# Test the feature engineering
# ==============================================

if __name__ == "__main__":

    df = create_features()

    print("\n========================================")
    print("FEATURE ENGINEERING")
    print("========================================")

    print("\nDataset shape:")
    print(df.shape)

    print("\nMonthly pattern features:")

    monthly_features = [
        "case_id",
        "first_month_payment",
        "last_month_payment",
        "first_to_last_change",
        "first_to_last_change_pct",
        "high_payment_months",
        "months_above_award",
        "largest_monthly_increase",
        "largest_monthly_decrease"
    ]

    print(
        df[monthly_features]
        .head(10)
        .to_string(index=False)
    )

    print("\n========================================")
    print("FEATURE STATISTICS")
    print("========================================")

    statistics_features = [
        "average_payment_to_award_ratio",
        "maximum_payment_to_award_ratio",
        "payment_variability",
        "adjustment_rate",
        "award_to_needs_ratio",
        "first_to_last_change_pct",
        "high_payment_months",
        "months_above_award"
    ]

    print(
        df[statistics_features].describe()
    )

    print("\n========================================")
    print("TOP CASES BY HIGH-PAYMENT MONTHS")
    print("========================================")

    print(
        df.nlargest(10, "high_payment_months")[
            [
                "case_id",
                "monthly_award",
                "average_payment",
                "maximum_payment",
                "high_payment_months",
                "months_above_award"
            ]
        ].to_string(index=False)
    )

    print("\n========================================")
    print("FEATURE ENGINEERING COMPLETE")
    print("========================================")