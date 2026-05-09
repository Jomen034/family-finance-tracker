# app.py

import streamlit as st
import pandas as pd
import time
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

from utils.formatter import format_rupiah

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

    password = st.text_input(
        "Enter Password",
        type="password",
    )

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

    transactions_df["date"] = pd.to_datetime(
        transactions_df["date"]
    )

    current_month = datetime.now().month
    current_year = datetime.now().year

    current_df = transactions_df[
        (transactions_df["date"].dt.month == current_month)
        & (transactions_df["date"].dt.year == current_year)
    ]

    income = current_df[
        current_df["category"] == "income"
    ]["amount"].sum()

    expense = current_df[
        current_df["category"] == "expense"
    ]["amount"].sum()

    saving = income - expense

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Income",
        format_rupiah(income),
    )

    col2.metric(
        "Expense",
        format_rupiah(expense),
    )

    col3.metric(
        "Saving",
        format_rupiah(saving),
    )

    st.divider()

    st.subheader("Recent Transactions")

    display_df = current_df.copy()

    display_df["amount"] = display_df["amount"].apply(
        format_rupiah
    )

    st.dataframe(
        display_df.sort_values(
            "date",
            ascending=False,
        ),
        use_container_width=True,
    )

# =========================
# ADD TRANSACTION
# =========================

elif page == "Add Transaction":

    st.title("➕ Add Transaction")

    if transaction_names_df.empty:
        st.warning(
            "master_transaction_names is empty."
        )
        st.stop()

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

        description = st.text_area(
            "Description"
        )

        submitted = st.form_submit_button(
            "Save Transaction"
        )

        if submitted:

            add_transaction(
                {
                    "date": str(date),
                    "name": transaction_name,
                    "category": category,
                    "amount": int(amount),
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                }
            )

            st.success(
                "Transaction added successfully!"
            )
            time.sleep(1.5)
            st.rerun()

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
        + transactions_df["name"]
        + " | "
        + transactions_df["amount"].apply(
            format_rupiah
        )
    )

    selected_label = st.selectbox(
        "Select Transaction",
        transactions_df["label"].tolist(),
    )

    selected_row = transactions_df[
        transactions_df["label"]
        == selected_label
    ].iloc[0]

    with st.form("edit_transaction_form"):

        edit_date = st.date_input(
            "Date",
            pd.to_datetime(
                selected_row["date"]
            ),
        )

        selected_name_index = 0

        matching_index = transaction_names_df[
            transaction_names_df["name"]
            == selected_row["name"]
        ]

        if not matching_index.empty:
            selected_name_index = (
                matching_index.index[0]
            )

        edit_name = st.selectbox(
            "Transaction Name",
            transaction_names_df["name"].tolist(),
            index=selected_name_index,
        )

        categories = [
            "expense",
            "income",
            "transfer/topup",
            "cash withdrawal",
        ]

        selected_category_index = 0

        if (
            selected_row["category"]
            in categories
        ):
            selected_category_index = (
                categories.index(
                    selected_row["category"]
                )
            )

        edit_category = st.selectbox(
            "Category",
            categories,
            index=selected_category_index,
        )

        edit_amount = st.number_input(
            "Amount",
            min_value=0,
            value=int(selected_row["amount"]),
            step=1000,
        )

        edit_description = st.text_area(
            "Description",
            value=selected_row["description"],
        )

        update_submitted = (
            st.form_submit_button(
                "Update Transaction"
            )
        )

        if update_submitted:

            update_transaction(
                selected_row["id"],
                {
                    "date": str(edit_date),
                    "name": edit_name,
                    "category": edit_category,
                    "amount": int(edit_amount),
                    "description": edit_description,
                },
            )

            st.success(
                "Transaction updated successfully!"
            )
            time.sleep(1.5)
            st.rerun()

# =========================
# BUDGETING
# =========================

elif page == "Budgeting":

    st.title("🎯 Budgeting")

    if not budget_df.empty:

        display_budget = budget_df.copy()

        display_budget[
            "monthly_budget"
        ] = display_budget[
            "monthly_budget"
        ].apply(format_rupiah)

        st.dataframe(
            display_budget,
            use_container_width=True,
        )

    st.divider()

    st.subheader("Add / Update Budget")

    if transaction_names_df.empty:

        st.warning(
            "No transaction names available."
        )

        st.stop()

    with st.form("budget_form"):

        selected_name = st.selectbox(
            "Transaction Name",
            transaction_names_df["name"].tolist(),
        )

        monthly_budget = st.number_input(
            "Monthly Budget",
            min_value=0,
            step=100000,
        )

        budget_submit = (
            st.form_submit_button(
                "Save Budget"
            )
        )

        if budget_submit:

            update_budget_data(
                selected_name,
                int(monthly_budget),
            )

            st.success(
                "Budget updated!"
            )
            time.sleep(1.5)
            st.rerun()

# =========================
# ANALYTICS
# =========================

elif page == "Analytics":

    st.title("📈 Analytics")

    daily = daily_summary(
        transactions_df
    )

    weekly = weekly_summary(
        transactions_df
    )

    monthly = monthly_summary(
        transactions_df
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Daily",
            "Weekly",
            "Monthly",
        ]
    )

    with tab1:
        st.dataframe(
            daily,
            use_container_width=True,
        )

    with tab2:
        st.dataframe(
            weekly,
            use_container_width=True,
        )

    with tab3:
        st.dataframe(
            monthly,
            use_container_width=True,
        )

    st.divider()

    st.subheader(
        "Budget vs Actual"
    )

    budget_actual = budget_vs_actual(
        transactions_df,
        budget_df,
    )

    if not budget_actual.empty:

        budget_actual[
            "amount"
        ] = budget_actual[
            "amount"
        ].apply(format_rupiah)

        budget_actual[
            "monthly_budget"
        ] = budget_actual[
            "monthly_budget"
        ].apply(format_rupiah)

    st.dataframe(
        budget_actual,
        use_container_width=True,
    )