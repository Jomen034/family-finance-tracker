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
    get_accounts,
)

from services.analytics_service import (
    daily_summary,
    weekly_summary,
    monthly_summary,
    budget_vs_actual,
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
# CUSTOM UI
# =========================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 100px;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.3rem;
    }

    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 26px;
        border-radius: 18px;
        border: none;
        background-color: #1F2937;
    }

    div.stButton > button:hover {
        background-color: #374151;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# WELCOME
# =========================

st.title("💰 GFams Finance Tracker")

st.caption(
    "Simple family finance tracker for daily household expenses."
)

st.divider()

# =========================
# LOAD DATA
# =========================

transactions_df = get_transactions()

transaction_names_df = get_transaction_names()

budget_df = get_budget_data()

accounts_df = get_accounts()

# =========================
# DATA CLEANING
# =========================

if not transactions_df.empty:

    transactions_df["amount"] = pd.to_numeric(
        transactions_df["amount"],
        errors="coerce",
    ).fillna(0)

    transactions_df["date"] = pd.to_datetime(
        transactions_df["date"],
        errors="coerce",
    )

# =========================
# MOBILE NAVIGATION
# =========================

query_params = st.query_params

if "page" not in query_params:
    st.query_params["page"] = "dashboard"

selected_tab = st.query_params["page"]

st.markdown(
    f"""
    <style>

    .bottom-nav {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 75px;
        background-color: #111827;
        border-top: 1px solid #374151;

        display: flex;
        justify-content: space-around;
        align-items: center;

        z-index: 999999;
    }}

    .bottom-nav a {{
        text-decoration: none;
        font-size: 28px;
        color: #9CA3AF;
    }}

    .bottom-nav a.active {{
        color: #F87171;
    }}

    </style>

    <div class="bottom-nav">

        <a href="?page=dashboard"
           class="{"active" if selected_tab == "dashboard" else ""}">
           🏠
        </a>

        <a href="?page=add"
           class="{"active" if selected_tab == "add" else ""}">
           ➕
        </a>

        <a href="?page=edit"
           class="{"active" if selected_tab == "edit" else ""}">
           ✏️
        </a>

        <a href="?page=budget"
           class="{"active" if selected_tab == "budget" else ""}">
           💰
        </a>

        <a href="?page=analytics"
           class="{"active" if selected_tab == "analytics" else ""}">
           📊
        </a>

    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# DASHBOARD
# =========================

if selected_tab == "dashboard":

    st.title("📊 Dashboard")

    if transactions_df.empty:
        st.warning("No transaction data yet.")
        st.stop()

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

    transaction_count = len(current_df)

    # =========================
    # METRICS
    # =========================

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "💵 Income",
            f"Rp {income:,.0f}",
        )

    with col2:
        st.metric(
            "💸 Expense",
            f"Rp {expense:,.0f}",
        )

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "🏦 Saving",
            f"Rp {saving:,.0f}",
        )

    with col4:
        st.metric(
            "🧾 Transactions",
            transaction_count,
        )

    st.divider()

    # =========================
    # ACCOUNT USAGE
    # =========================

    st.subheader("🏦 Account Usage")

    if (
        "account" in current_df.columns
        and not current_df.empty
    ):

        account_summary = (
            current_df.groupby("account")
            .agg(
                total_amount=("amount", "sum"),
                total_transactions=("account", "count"),
            )
            .reset_index()
            .sort_values(
                "total_amount",
                ascending=False,
            )
        )

        account_summary["total_amount"] = (
            account_summary["total_amount"]
            .apply(
                lambda x: f"Rp {x:,.0f}"
            )
        )

        st.dataframe(
            account_summary,
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # =========================
    # RECENT TRANSACTIONS
    # =========================

    st.subheader("🧾 Recent Transactions")

    recent_df = current_df.sort_values(
        "date",
        ascending=False,
    )

    st.dataframe(
        recent_df,
        use_container_width=True,
        hide_index=True,
    )

# =========================
# ADD TRANSACTION
# =========================

elif selected_tab == "add":

    st.title("➕ Add Transaction")

    with st.form(
        "add_transaction_form",
        clear_on_submit=True,
    ):

        date = st.date_input("Date")

        transaction_name = st.selectbox(
            "Transaction Name",
            transaction_names_df[
                "name"
            ].tolist(),
        )

        account = st.selectbox(
            "Account",
            accounts_df[
                "account_name"
            ].tolist(),
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
                    "account": account,
                    "category": category,
                    "amount": int(amount),
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                }
            )

            st.success(
                "✅ Transaction added successfully!"
            )

            st.rerun()

# =========================
# EDIT TRANSACTION
# =========================

elif selected_tab == "edit":

    st.title("✏️ Edit Transaction")

    if transactions_df.empty:
        st.warning("No transaction data.")
        st.stop()

    transactions_df["label"] = (
        transactions_df["date"]
        .astype(str)
        + " | "
        + transactions_df["name"]
        + " | Rp "
        + transactions_df["amount"]
        .astype(int)
        .astype(str)
    )

    selected_label = st.selectbox(
        "Select Transaction",
        transactions_df[
            "label"
        ].tolist(),
    )

    selected_row = transactions_df[
        transactions_df["label"]
        == selected_label
    ].iloc[0]

    with st.form(
        "edit_transaction_form"
    ):

        edit_date = st.date_input(
            "Date",
            pd.to_datetime(
                selected_row["date"]
            ),
        )

        edit_name = st.selectbox(
            "Transaction Name",
            transaction_names_df[
                "name"
            ].tolist(),
            index=transaction_names_df[
                transaction_names_df[
                    "name"
                ]
                == selected_row["name"]
            ].index[0],
        )

        account_list = accounts_df[
            "account_name"
        ].tolist()

        current_account = (
            selected_row["account"]
            if "account" in selected_row
            else account_list[0]
        )

        account_index = (
            account_list.index(current_account)
            if current_account in account_list
            else 0
        )

        edit_account = st.selectbox(
            "Account",
            account_list,
            index=account_index,
        )

        category_options = [
            "expense",
            "income",
            "transfer/topup",
            "cash withdrawal",
        ]

        category_index = (
            category_options.index(
                selected_row["category"]
            )
            if selected_row["category"]
            in category_options
            else 0
        )

        edit_category = st.selectbox(
            "Category",
            category_options,
            index=category_index,
        )

        edit_amount = st.number_input(
            "Amount",
            value=int(
                selected_row["amount"]
            ),
        )

        edit_description = st.text_area(
            "Description",
            value=selected_row[
                "description"
            ],
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
                    "account": edit_account,
                    "category": edit_category,
                    "amount": int(edit_amount),
                    "description": edit_description,
                },
            )

            st.success(
                "✅ Transaction updated successfully!"
            )

            st.rerun()

# =========================
# BUDGETING
# =========================

elif selected_tab == "budget":

    st.title("🎯 Budgeting")

    st.subheader(
        "Current Budget Setup"
    )

    st.dataframe(
        budget_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    with st.form(
        "budget_form",
        clear_on_submit=True,
    ):

        selected_name = st.selectbox(
            "Transaction Name",
            transaction_names_df[
                "name"
            ].tolist(),
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
                "Save Budget"
            )
        )

        if budget_submit:

            update_budget_data(
                selected_name,
                int(monthly_budget),
            )

            st.success(
                "✅ Budget updated successfully!"
            )

            st.rerun()

# =========================
# ANALYTICS
# =========================

elif selected_tab == "analytics":

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

    budget_actual = budget_vs_actual(
        transactions_df,
        budget_df,
    )

    st.dataframe(
        budget_actual,
        use_container_width=True,
        hide_index=True,
    )