# app.py

import time
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_option_menu import option_menu

from services.sheets_service import (
    get_transactions,
    add_transaction,
    update_transaction,
    get_transaction_names,
    get_budget_data,
    update_budget_data,
    get_accounts,
)

from services.analytics_service import (
    monthly_summary,
    weekly_summary,
    daily_summary,
    budget_vs_actual,
    expense_trend,
    expense_by_name,
    monthly_kpi,
    account_summary,
)

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="GFams Finance Tracker",
    page_icon="💰",
    layout="wide",
)

# =========================
# WELCOME SCREEN
# =========================

if "entered_app" not in st.session_state:
    st.session_state.entered_app = False

if not st.session_state.entered_app:

    st.markdown(
        """
        # 💰 GFams Finance Tracker

        Welcome to your family financial dashboard.

        Track:
        - expenses
        - income
        - budgeting
        - account usage
        - spending analytics

        Built for simple daily family finance management ❤️
        """
    )

    st.divider()

    if st.button(
        "🚀 Continue to App",
        use_container_width=True,
        type="primary",
    ):

        st.session_state.entered_app = True
        st.rerun()

    st.stop()

# =========================
# LOAD DATA
# =========================

transactions_df = get_transactions()

transaction_names_df = (
    get_transaction_names()
)

budget_df = get_budget_data()

accounts_df = get_accounts()

# =========================
# BOTTOM NAVIGATION
# =========================

page = option_menu(
    menu_title=None,
    options=[
        "Dashboard",
        "Add",
        "Edit",
        "Budget",
        "Analytics",
    ],
    icons=[
        "house",
        "plus-circle",
        "pencil-square",
        "wallet2",
        "bar-chart",
    ],
    orientation="horizontal",
    default_index=0,
)

# =========================
# DASHBOARD
# =========================

if page == "Dashboard":

    st.title("📊 Dashboard")

    if transactions_df.empty:

        st.warning(
            "No transaction data yet."
        )

        st.stop()

    # =========================
    # KPI
    # =========================

    kpi = monthly_kpi(
        transactions_df
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "💵 Income",
            f"Rp {kpi['income']:,.0f}",
        )

    with col2:

        st.metric(
            "💸 Expense",
            f"Rp {kpi['expense']:,.0f}",
        )

    col3, col4 = st.columns(2)

    with col3:

        st.metric(
            "🏦 Saving",
            f"Rp {kpi['saving']:,.0f}",
        )

    with col4:

        st.metric(
            "🧾 Transactions",
            kpi["total_transactions"],
        )

    st.divider()

    # =========================
    # EXPENSE TREND
    # =========================

    st.subheader(
        "📈 Expense Trend"
    )

    trend_df = expense_trend(
        transactions_df
    )

    if not trend_df.empty:

        fig_trend = px.line(
            trend_df,
            x="date",
            y="expense_amount",
            markers=True,
            title="Daily Expense Trend",
        )

        st.plotly_chart(
            fig_trend,
            use_container_width=True,
        )

    # =========================
    # EXPENSE BY NAME
    # =========================

    st.subheader(
        "💳 Expense by Name"
    )

    expense_name_df = (
        expense_by_name(
            transactions_df
        )
    )

    if not expense_name_df.empty:

        fig_expense_name = px.bar(
            expense_name_df,
            x="name",
            y="expense_amount",
            title="Expense by Transaction Name",
        )

        st.plotly_chart(
            fig_expense_name,
            use_container_width=True,
        )

    # =========================
    # ACCOUNT USAGE
    # =========================

    st.subheader(
        "🏦 Account Usage"
    )

    account_df = account_summary(
        transactions_df
    )

    if not account_df.empty:

        fig_account = px.bar(
            account_df,
            x="account",
            y="total_amount",
            title="Usage by Account",
            hover_data=[
                "total_transactions"
            ],
        )

        st.plotly_chart(
            fig_account,
            use_container_width=True,
        )

        display_account_df = (
            account_df.copy()
        )

        display_account_df[
            "total_amount"
        ] = (
            display_account_df[
                "total_amount"
            ]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

        st.dataframe(
            display_account_df,
            use_container_width=True,
            hide_index=True,
        )

    # =========================
    # BUDGET VS ACTUAL
    # =========================

    st.subheader(
        "🎯 Budget vs Actual"
    )

    budget_actual_df = (
        budget_vs_actual(
            transactions_df,
            budget_df,
        )
    )

    if not budget_actual_df.empty:

        fig_budget = px.bar(
            budget_actual_df,
            x="name",
            y=[
                "amount",
                "monthly_budget",
            ],
            barmode="group",
            title="Budget vs Actual",
        )

        st.plotly_chart(
            fig_budget,
            use_container_width=True,
        )

    st.divider()

    # =========================
    # RECENT TRANSACTIONS
    # =========================

    st.subheader(
        "🕒 Recent Transactions"
    )

    recent_df = (
        transactions_df
        .sort_values(
            "date",
            ascending=False,
        )
        .head(10)
    )

    display_df = recent_df.copy()

    display_df["amount"] = (
        display_df["amount"]
        .apply(
            lambda x:
            f"Rp {x:,.0f}"
        )
    )

    st.dataframe(
        display_df[
            [
                "date",
                "name",
                "category",
                "account",
                "amount",
                "description",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

# =========================
# ADD TRANSACTION
# =========================

elif page == "Add":

    st.title(
        "➕ Add Transaction"
    )

    with st.form(
        "add_transaction_form",
        clear_on_submit=True,
    ):

        date = st.date_input(
            "Date"
        )

        transaction_name = (
            st.selectbox(
                "Transaction Name",
                transaction_names_df[
                    "name"
                ].tolist(),
            )
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

        account = st.selectbox(
            "Account",
            accounts_df[
                "account_name"
            ].tolist(),
        )

        amount = st.number_input(
            "Amount",
            min_value=0,
            step=1000,
        )

        description = st.text_area(
            "Description"
        )

        submitted = (
            st.form_submit_button(
                "Save Transaction",
                use_container_width=True,
            )
        )

        if submitted:

            add_transaction(
                {
                    "date": str(date),
                    "name": transaction_name,
                    "category": category,
                    "account": account,
                    "amount": amount,
                    "description": description,
                    "created_at": (
                        datetime.now()
                        .isoformat()
                    ),
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

elif page == "Edit":

    st.title(
        "✏️ Edit Transaction"
    )

    if transactions_df.empty:

        st.warning(
            "No transaction data."
        )

        st.stop()

    transactions_df["label"] = (
        transactions_df["date"]
        .astype(str)
        + " | "
        + transactions_df["name"]
        + " | Rp "
        + transactions_df["amount"]
        .astype(str)
    )

    selected_label = st.selectbox(
        "Select Transaction",
        transactions_df[
            "label"
        ].tolist(),
    )

    selected_row = (
        transactions_df[
            transactions_df["label"]
            == selected_label
        ]
        .iloc[0]
    )

    with st.form(
        "edit_transaction_form"
    ):

        edit_date = st.date_input(
            "Date",
            pd.to_datetime(
                selected_row["date"]
            ),
        )

        name_options = (
            transaction_names_df[
                "name"
            ].tolist()
        )

        current_name = (
            selected_row["name"]
        )

        current_index = (
            name_options.index(
                current_name
            )
            if current_name
            in name_options
            else 0
        )

        edit_name = st.selectbox(
            "Transaction Name",
            name_options,
            index=current_index,
        )

        category_options = [
            "expense",
            "income",
            "transfer/topup",
            "cash withdrawal",
        ]

        current_category = (
            selected_row["category"]
        )

        category_index = (
            category_options.index(
                current_category
            )
            if current_category
            in category_options
            else 0
        )

        edit_category = st.selectbox(
            "Category",
            category_options,
            index=category_index,
        )

        account_options = (
            accounts_df[
                "account_name"
            ].tolist()
        )

        current_account = (
            selected_row["account"]
        )

        account_index = (
            account_options.index(
                current_account
            )
            if current_account
            in account_options
            else 0
        )

        edit_account = st.selectbox(
            "Account",
            account_options,
            index=account_index,
        )

        edit_amount = st.number_input(
            "Amount",
            value=float(
                selected_row["amount"]
            ),
        )

        edit_description = (
            st.text_area(
                "Description",
                value=selected_row[
                    "description"
                ],
            )
        )

        update_submitted = (
            st.form_submit_button(
                "Update Transaction",
                use_container_width=True,
            )
        )

        if update_submitted:

            update_transaction(
                selected_row["id"],
                {
                    "date": str(
                        edit_date
                    ),
                    "name": edit_name,
                    "category": (
                        edit_category
                    ),
                    "account": (
                        edit_account
                    ),
                    "amount": (
                        edit_amount
                    ),
                    "description": (
                        edit_description
                    ),
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

elif page == "Budget":

    st.title("🎯 Budgeting")

    st.subheader(
        "Current Budget"
    )

    display_budget_df = (
        budget_df.copy()
    )

    if not display_budget_df.empty:

        display_budget_df[
            "monthly_budget"
        ] = (
            display_budget_df[
                "monthly_budget"
            ]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

    st.dataframe(
        display_budget_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    with st.form(
        "budget_form",
        clear_on_submit=True,
    ):

        selected_name = (
            st.selectbox(
                "Transaction Name",
                transaction_names_df[
                    "name"
                ].tolist(),
            )
        )

        monthly_budget = (
            st.number_input(
                "Monthly Budget",
                min_value=0,
                step=100000,
            )
        )

        budget_submit = (
            st.form_submit_button(
                "Save Budget",
                use_container_width=True,
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
            hide_index=True,
        )

    with tab2:

        st.dataframe(
            weekly,
            use_container_width=True,
            hide_index=True,
        )

    with tab3:

        st.dataframe(
            monthly,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    st.subheader(
        "🎯 Budget vs Actual"
    )

    budget_actual = (
        budget_vs_actual(
            transactions_df,
            budget_df,
        )
    )

    if not budget_actual.empty:

        display_budget_actual = (
            budget_actual.copy()
        )

        display_budget_actual[
            "amount"
        ] = (
            display_budget_actual[
                "amount"
            ]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

        display_budget_actual[
            "monthly_budget"
        ] = (
            display_budget_actual[
                "monthly_budget"
            ]
            .apply(
                lambda x:
                f"Rp {x:,.0f}"
            )
        )

        display_budget_actual[
            "usage_percentage"
        ] = (
            display_budget_actual[
                "usage_percentage"
            ]
            .apply(
                lambda x:
                f"{x:.2f}%"
            )
        )

        st.dataframe(
            display_budget_actual,
            use_container_width=True,
            hide_index=True,
        )
