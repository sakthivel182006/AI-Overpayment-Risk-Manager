import pandas as pd


def load_data():
    cases = pd.read_csv("data/cases.csv")
    payments = pd.read_csv("data/payments.csv")

    return cases, payments


if __name__ == "__main__":
    cases, payments = load_data()

    print("Cases shape:", cases.shape)
    print("Payments shape:", payments.shape)

    print("\nCases:")
    print(cases.head())

    print("\nPayments:")
    print(payments.head())