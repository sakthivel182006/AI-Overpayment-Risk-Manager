import pandas as pd


NEEDS_FIGURE = {
    1: 1240,
    2: 1670,
    3: 2000,
    4: 2330,
    5: 2660,
    6: 2990
}


def analyze_patterns():

    # Load data
    cases = pd.read_csv("data/cases.csv")
    payments = pd.read_csv("data/payments.csv")

    # Convert dates
    payments["pay_month"] = pd.to_datetime(payments["pay_month"])

    # Aggregate payment information for each case
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

    # Merge case and payment information
    df = cases.merge(
        payment_summary,
        on="case_id",
        how="left"
    )

    # Fill missing standard deviation
    df["payment_std"] = df["payment_std"].fillna(0)

    # Needs figure based on household size
    df["needs_figure"] = df["household_size"].map(NEEDS_FIGURE)

    # Useful ratios
    df["payment_to_award_ratio"] = (
        df["average_payment"] / df["monthly_award"]
    )

    df["total_to_award_ratio"] = (
        df["total_paid"] /
        (df["monthly_award"] * df["payment_count"])
    )

    df["maximum_to_award_ratio"] = (
        df["maximum_payment"] /
        df["monthly_award"]
    )

    df["adjustment_rate"] = (
        df["adjustment_payment_count"] /
        df["payment_count"]
    )

    print("\n========================================")
    print("OVERPAYMENT PATTERN ANALYSIS")
    print("========================================")

    print("\nTotal cases:", len(df))
    print("Total payments:", len(payments))

    print("\nPayment count distribution:")
    print(df["payment_count"].value_counts().sort_index())

    print("\nTop 10 cases by total/award ratio:")
    print(
        df.nlargest(10, "total_to_award_ratio")[
            [
                "case_id",
                "household_size",
                "monthly_award",
                "total_paid",
                "payment_count",
                "total_to_award_ratio"
            ]
        ].to_string(index=False)
    )

    print("\nTop 10 cases by maximum payment/award ratio:")
    print(
        df.nlargest(10, "maximum_to_award_ratio")[
            [
                "case_id",
                "monthly_award",
                "maximum_payment",
                "maximum_to_award_ratio",
                "payment_adjustments",
                "contact_attempts"
            ]
        ].to_string(index=False)
    )

    print("\nTop 10 cases by payment variability:")
    print(
        df.nlargest(10, "payment_std")[
            [
                "case_id",
                "monthly_award",
                "payment_std",
                "payment_count",
                "payment_adjustments"
            ]
        ].to_string(index=False)
    )

    print("\nTop 10 cases by payment adjustments:")
    print(
        df.nlargest(10, "payment_adjustments")[
            [
                "case_id",
                "payment_adjustments",
                "adjustment_payment_count",
                "adjustment_rate",
                "contact_attempts"
            ]
        ].to_string(index=False)
    )

    print("\n========================================")
    print("ANALYSIS COMPLETE")
    print("========================================")


if __name__ == "__main__":
    analyze_patterns()