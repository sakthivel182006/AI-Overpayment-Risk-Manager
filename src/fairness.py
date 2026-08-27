import pandas as pd

from risk_scoring import calculate_risk_score
from feature_engineering import create_features


# Number of cases we send to investigators
TOP_N = 20


def calculate_fairness(df, column):
    """
    Analyse how the risk ranking behaves across one demographic field.
    """

    total_cases = len(df)

    # Overall rate of cases selected for review
    overall_rate = TOP_N / total_cases

    results = []

    for group, group_df in df.groupby(column, dropna=False):

        group_size = len(group_df)

        # Number of TOP 20 cases from this group
        top_cases = group_df["review_priority"].sum()

        # Percentage of the group appearing in TOP 20
        selection_rate = top_cases / group_size

        # Representation of this group inside TOP 20
        top20_percentage = (
            top_cases / TOP_N
        ) * 100

        # Ratio compared with the overall population rate
        if overall_rate > 0:
            selection_rate_ratio = (
                selection_rate / overall_rate
            )
        else:
            selection_rate_ratio = 0

        results.append({
            "group": group,
            "population_count": group_size,
            "top20_count": int(top_cases),
            "selection_rate": round(selection_rate * 100, 2),
            "top20_percentage": round(top20_percentage, 2),
            "selection_rate_ratio": round(
                selection_rate_ratio, 2
            )
        })

    return pd.DataFrame(results)


def run_fairness_analysis():

    print("\n========================================")
    print("FAIRNESS ANALYSIS")
    print("========================================")

    # --------------------------------------
    # Create features
    # --------------------------------------

    df = create_features()

    # --------------------------------------
    # Calculate risk score
    # --------------------------------------

    df = calculate_risk_score(df)

    # --------------------------------------
    # Rank cases
    # --------------------------------------

    df = df.sort_values(
        by="risk_score",
        ascending=False
    ).reset_index(drop=True)

    # --------------------------------------
    # Mark TOP 20
    # --------------------------------------

    df["review_priority"] = 0

    df.loc[
        df.index[:TOP_N],
        "review_priority"
    ] = 1

    # --------------------------------------
    # Demographic fields required
    # by the problem statement
    # --------------------------------------

    demographic_fields = [
        "age_band",
        "language_preference",
        "district",
        "tenure"
    ]

    all_results = []

    # --------------------------------------
    # Analyse each demographic field
    # --------------------------------------

    for column in demographic_fields:

        print("\n----------------------------------------")
        print(f"FAIRNESS CHECK: {column}")
        print("----------------------------------------")

        result = calculate_fairness(
            df,
            column
        )

        result.insert(
            0,
            "dimension",
            column
        )

        all_results.append(result)

        print(
            result.to_string(index=False)
        )

    # --------------------------------------
    # Combine all results
    # --------------------------------------

    fairness_report = pd.concat(
        all_results,
        ignore_index=True
    )

    # --------------------------------------
    # Save report
    # --------------------------------------

    import os

    os.makedirs(
        "outputs",
        exist_ok=True
    )

    fairness_report.to_csv(
        "outputs/fairness_report.csv",
        index=False
    )

    # --------------------------------------
    # Summary
    # --------------------------------------

    print("\n========================================")
    print("FAIRNESS SUMMARY")
    print("========================================")

    print(
        fairness_report[
            [
                "dimension",
                "group",
                "population_count",
                "top20_count",
                "selection_rate",
                "selection_rate_ratio"
            ]
        ].to_string(index=False)
    )

    print("\nFairness report saved to:")
    print("outputs/fairness_report.csv")

    print("\n========================================")
    print("FAIRNESS ANALYSIS COMPLETE")
    print("========================================")

    return fairness_report


if __name__ == "__main__":
    run_fairness_analysis()