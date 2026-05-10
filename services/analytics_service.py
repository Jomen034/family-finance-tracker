# services/analytics_service.py

import pandas as pd
import streamlit as st


# =========================
# DAILY SUMMARY
# =========================

@st.cache_data(ttl=30)
def daily_summary(df):

    if df.empty:
        return pd.DataFrame()

    temp_df = df.copy()

    result = (
        temp_df.groupby(
            temp_df["date"].dt.date
        )["amount"]
        .sum()
        .reset_index()
    )

    result.columns = [
        "date",
        "total_amount",
    ]

    return result


# =========================
# WEEKLY SUMMARY
# =========================

@st.cache_data(ttl=30)
def weekly_summary(df):

    if df.empty:
        return pd.DataFrame()

    temp_df = df.copy()

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

    result.columns = [
        "week",
        "total_amount",
    ]

    return result


# =========================
# MONTHLY SUMMARY
# =========================

@st.cache_data(ttl=30)
def monthly_summary(df):

    if df.empty:
        return pd.DataFrame()

    temp_df = df.copy()

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

    result.columns = [
        "month",
        "total_amount",
    ]

    return result


# =========================
# BUDGET VS ACTUAL
# =========================

@st.cache_data(ttl=30)
def budget_vs_actual(
    transactions_df,
    budget_df,
):

    if (
        transactions_df.empty
        or budget_df.empty
    ):
        return pd.DataFrame()

    expense_df = transactions_df.copy()

    expense_df.columns = (
        expense_df.columns.str.strip()
    )

    budget_df.columns = (
        budget_df.columns.str.strip()
    )

    # EXPENSE ONLY
    expense_df = expense_df[
        expense_df["category"]
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
        on="name",
        how="left",
    )

    merged["monthly_budget"] = (
        pd.to_numeric(
            merged["monthly_budget"],
            errors="coerce",
        )
        .fillna(0)
    )

    merged["usage_percentage"] = (
        (
            merged["amount"]
            / merged["monthly_budget"]
        )
        * 100
    ).replace(
        [float("inf")],
        0,
    ).fillna(0)

    merged["usage_percentage"] = (
        merged["usage_percentage"]
        .round(2)
    )

    return merged.sort_values(
        "amount",
        ascending=False,
    )


# =========================
# EXPENSE TREND
# =========================

@st.cache_data(ttl=30)
def expense_trend(df):

    if df.empty:
        return pd.DataFrame()

    expense_df = df[
        df["category"]
        == "expense"
    ].copy()

    result = (
        expense_df.groupby("date")[
            "amount"
        ]
        .sum()
        .reset_index()
    )

    result.columns = [
        "date",
        "expense_amount",
    ]

    return result.sort_values(
        "date"
    )


# =========================
# EXPENSE BY NAME
# =========================

@st.cache_data(ttl=30)
def expense_by_name(df):

    if df.empty:
        return pd.DataFrame()

    expense_df = df[
        df["category"]
        == "expense"
    ].copy()

    result = (
        expense_df.groupby("name")[
            "amount"
        ]
        .sum()
        .reset_index()
    )

    result.columns = [
        "name",
        "expense_amount",
    ]

    return result.sort_values(
        "expense_amount",
        ascending=False,
    )


# =========================
# MONTHLY KPI
# =========================

@st.cache_data(ttl=30)
def monthly_kpi(df):

    if df.empty:
        return {
            "income": 0,
            "expense": 0,
            "saving": 0,
            "total_transactions": 0,
        }

    temp_df = df.copy()

    current_month = (
        pd.Timestamp.now().month
    )

    current_year = (
        pd.Timestamp.now().year
    )

    current_df = temp_df[
        (
            temp_df["date"].dt.month
            == current_month
        )
        &
        (
            temp_df["date"].dt.year
            == current_year
        )
    ]

    income = current_df[
        current_df["category"]
        == "income"
    ]["amount"].sum()

    expense = current_df[
        current_df["category"]
        == "expense"
    ]["amount"].sum()

    saving = income - expense

    total_transactions = len(
        current_df
    )

    return {
        "income": income,
        "expense": expense,
        "saving": saving,
        "total_transactions": total_transactions,
    }