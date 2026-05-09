# services/analytics_service.py

import pandas as pd


def daily_summary(df):

    if df.empty:
        return pd.DataFrame()

    temp_df = df.copy()

    temp_df["date"] = pd.to_datetime(
        temp_df["date"]
    )

    result = (
        temp_df.groupby(
            temp_df["date"].dt.date
        )["amount"]
        .sum()
        .reset_index()
    )

    return result


def weekly_summary(df):

    if df.empty:
        return pd.DataFrame()

    temp_df = df.copy()

    temp_df["date"] = pd.to_datetime(
        temp_df["date"]
    )

    temp_df["week"] = (
        temp_df["date"]
        .dt.isocalendar()
        .week
    )

    result = (
        temp_df.groupby("week")[
            "amount"
        ]
        .sum()
        .reset_index()
    )

    return result


def monthly_summary(df):

    if df.empty:
        return pd.DataFrame()

    temp_df = df.copy()

    temp_df["date"] = pd.to_datetime(
        temp_df["date"]
    )

    temp_df["month"] = (
        temp_df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    result = (
        temp_df.groupby("month")[
            "amount"
        ]
        .sum()
        .reset_index()
    )

    return result


def budget_vs_actual(
    transactions_df,
    budget_df,
):

    if (
        transactions_df.empty
        or budget_df.empty
    ):
        return pd.DataFrame()

    expense_df = transactions_df[
        transactions_df["category"]
        == "expense"
    ]

    actual = (
        expense_df.groupby("name")[
            "amount"
        ]
        .sum()
        .reset_index()
    )

    merged = actual.merge(
        budget_df,
        left_on="name",
        right_on="category",
        how="left",
    )

    merged["monthly_budget"] = (
        pd.to_numeric(
            merged["monthly_budget"],
            errors="coerce",
        ).fillna(0)
    )

    merged["usage_percentage"] = (
        (
            merged["amount"]
            / merged["monthly_budget"]
        )
        * 100
    ).fillna(0)

    merged["usage_percentage"] = (
        merged["usage_percentage"]
        .round(2)
    )

    return merged