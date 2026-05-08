# app.py

import streamlit as st
import pandas as pd
from datetime import datetime
from services.sheets_service import (
    get_transactions,
    add_transaction,
    update_transaction,
    get_transaction_names,
    get_budget_data,
    update_budget_data,
)
from services.analytics_service import (
    monthly_summary,
    weekly_summary,
    daily_summary,
    budget_vs_actual,
)

st.set_page_config(
    page_title="Family Finance Tracker",
    page_icon="💰",
    layout="wide",
)

# =========================
# AUTH
# =========================
APP_PASSWORD = st.secrets["app"]["password"]

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 Family Finance Tracker")

    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        if password == APP_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid password")

    st.stop()

# =========================
# LOAD DATA
# =========================
transactions_df = get_transactions()

if not transactions_df.empty:

    transactions_df["amount"] = pd.to_numeric(
        transactions_df["amount"],
        errors="coerce",
    ).fillna(0)
    
transaction_names_df = get_transaction_names()
budget_df = get_budget_data()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("💰 Finance Tracker")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Add Transaction",
        "Edit Transaction",
        "Budgeting",
        "Analytics",
    ],
)

# =========================
# DASHBOARD
# =========================
if page == "Dashboard":

    st.title("📊 Dashboard")

    if transactions_df.empty:
        st.warning("No transaction data yet.")
        st.stop()

    current_month = datetime.now().month
    current_year = datetime.now().year

    transactions_df["date"] = pd.to_datetime(transactions_df["date"])

    current_df = transactions_df[
        (transactions_df["date"].dt.month == current_month)
        & (transactions_df["date"].dt.year == current_year)
    ]

    income = current_df[current_df["category"] == "income"]["amount"].sum()
    expense = current_df[current_df["category"] == "expense"]["amount"].sum()
    saving = income - expense

    col1, col2, col3 = st.columns(3)

    col1.metric("Income", f"Rp {income:,.0f}")
    col2.metric("Expense", f"Rp {expense:,.0f}")
    col3.metric("Saving", f"Rp {saving:,.0f}")

    st.divider()

    st.subheader("Recent Transactions")

    st.dataframe(
        current_df.sort_values("date", ascending=False),
        use_container_width=True,
    )

# =========================
# ADD TRANSACTION
# =========================
elif page == "Add Transaction":

    st.title("➕ Add Transaction")

    with st.form("add_transaction_form"):

        date = st.date_input("Date")

        transaction_name = st.selectbox(
            "Transaction Name",
            transaction_names_df["name"].tolist(),
        )

        category = st.selectbox(
            "Category",
            [
                "expense",
                "income",
                "transfer/topup",
                "cash withdrawal",
            ],
        )

        amount = st.number_input(
            "Amount",
            min_value=0,
            step=1000,
        )

        description = st.text_area("Description")

        submitted = st.form_submit_button("Save Transaction")

        if submitted:

            add_transaction(
                {
                    "date": str(date),
                    "transaction_name": transaction_name,
                    "category": category,
                    "amount": amount,
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                }
            )

            st.success("Transaction added successfully!")

# =========================
# EDIT TRANSACTION
# =========================
elif page == "Edit Transaction":

    st.title("✏️ Edit Transaction")

    if transactions_df.empty:
        st.warning("No transaction data.")
        st.stop()

    transactions_df["label"] = (
        transactions_df["date"].astype(str)
        + " | "
        + transactions_df["transaction_name"]
        + " | Rp "
        + transactions_df["amount"].astype(str)
    )

    selected_label = st.selectbox(
        "Select Transaction",
        transactions_df["label"].tolist(),
    )

    selected_row = transactions_df[
        transactions_df["label"] == selected_label
    ].iloc[0]

    with st.form("edit_transaction_form"):

        edit_date = st.date_input(
            "Date",
            pd.to_datetime(selected_row["date"]),
        )

        edit_name = st.selectbox(
            "Transaction Name",
            transaction_names_df["name"].tolist(),
            index=transaction_names_df[
                transaction_names_df["name"]
                == selected_row["transaction_name"]
            ].index[0],
        )

        edit_category = st.selectbox(
            "Category",
            [
                "expense",
                "income",
                "transfer/topup",
                "cash withdrawal",
            ],
        )

        edit_amount = st.number_input(
            "Amount",
            value=float(selected_row["amount"]),
        )

        edit_description = st.text_area(
            "Description",
            value=selected_row["description"],
        )

        update_submitted = st.form_submit_button("Update Transaction")

        if update_submitted:

            update_transaction(
                selected_row["id"],
                {
                    "date": str(edit_date),
                    "transaction_name": edit_name,
                    "category": edit_category,
                    "amount": edit_amount,
                    "description": edit_description,
                },
            )

            st.success("Transaction updated successfully!")

# =========================
# BUDGETING
# =========================
elif page == "Budgeting":

    st.title("🎯 Budgeting")

    st.dataframe(budget_df, use_container_width=True)

    with st.form("budget_form"):

        category = st.text_input("Category")
        monthly_budget = st.number_input(
            "Monthly Budget",
            min_value=0,
            step=100000,
        )

        budget_submit = st.form_submit_button("Save Budget")

        if budget_submit:

            update_budget_data(category, monthly_budget)

            st.success("Budget updated!")

# =========================
# ANALYTICS
# =========================
elif page == "Analytics":

    st.title("📈 Analytics")

    daily = daily_summary(transactions_df)
    weekly = weekly_summary(transactions_df)
    monthly = monthly_summary(transactions_df)

    tab1, tab2, tab3 = st.tabs(
        ["Daily", "Weekly", "Monthly"]
    )

    with tab1:
        st.dataframe(daily, use_container_width=True)

    with tab2:
        st.dataframe(weekly, use_container_width=True)

    with tab3:
        st.dataframe(monthly, use_container_width=True)

    st.divider()

    st.subheader("Budget vs Actual")

    budget_actual = budget_vs_actual(
        transactions_df,
        budget_df,
    )

    st.dataframe(budget_actual, use_container_width=True)
