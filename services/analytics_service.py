# services/analytics_service.py

import pandas as pd


def daily_summary(df):

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])

    result = (
        df.groupby(df["date"].dt.date)["amount"]
        .sum()
        .reset_index()
    )

    return result


def weekly_summary(df):

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])

    df["week"] = df["date"].dt.isocalendar().week

    result = (
        df.groupby("week")["amount"]
        .sum()
        .reset_index()
    )

    return result


def monthly_summary(df):

    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.to_period("M")

    result = (
        df.groupby("month")["amount"]
        .sum()
        .reset_index()
    )

    return result


def budget_vs_actual(transactions_df, budget_df):

    expense_df = transactions_df[
        transactions_df["category"] == "expense"
    ]

    actual = (
        expense_df.groupby("transaction_name")["amount"]
        .sum()
        .reset_index()
    )

    merged = actual.merge(
        budget_df,
        left_on="transaction_name",
        right_on="category",
        how="left",
    )

    merged["usage_percentage"] = (
        merged["amount"] / merged["monthly_budget"]
    ) * 100

    return merged
