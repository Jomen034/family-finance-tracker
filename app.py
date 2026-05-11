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
# HIDE STREAMLIT DEFAULT UI
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

    section[data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 120px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# WELCOME PAGE
# =========================

if "entered_app" not in st.session_state:
    st.session_state.entered_app = False

if not st.session_state.entered_app:

    st.markdown(
        """
        <div style="
            padding-top:80px;
            padding-bottom:40px;
        ">

        <h1 style="
            font-size:54px;
            margin-bottom:0;
            line-height:1.1;
        ">
            💰 GFams
        </h1>

        <h1 style="
            font-size:54px;
            margin-top:0;
            line-height:1.1;
        ">
            Finance Tracker
        </h1>

        <p style="
            color:gray;
            font-size:18px;
            margin-top:30px;
        ">
            Simple family finance tracker
            for daily household expenses.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Continue to App",
        use_container_width=True,
    ):
        st.session_state.entered_app = True
        st.rerun()

    st.stop()

# =========================
# LOAD DATA
# =========================

transactions_df = get_transactions()
transaction_names_df = get_transaction_names()
budget_df = get_budget_data()
accounts_df = get_accounts()

# =========================
# QUERY PARAMS NAVIGATION
# =========================

query_params = st.query_params

if "page" not in query_params:
    st.query_params["page"] = "dashboard"

current_page = st.query_params["page"]

page_map = {
    "dashboard": "Dashboard",
    "add": "Add Transaction",
    "edit": "Edit Transaction",
    "budget": "Budgeting",
    "analytics": "Analytics",
}

page = page_map.get(
    current_page,
    "Dashboard",
)

# =========================
# BOTTOM NAVIGATION
# =========================

st.markdown(
    f"""
    <style>

    .bottom-nav {{
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #0E1117;
        border-top: 1px solid #262730;
        padding-top: 12px;
        padding-bottom: 20px;
        z-index: 999999;
    }}

    .bottom-nav-container {{
        display: flex;
        justify-content: space-around;
        align-items: center;
    }}

    .nav-item {{
        text-decoration: none;
        font-size: 28px;
        opacity: 0.45;
    }}

    .nav-item.active {{
        opacity: 1;
        transform: scale(1.15);
    }}

    </style>

    <div class="bottom-nav">
        <div class="bottom-nav-container">

            <a href="?page=dashboard"
               class="nav-item {'active' if current_page == 'dashboard' else ''}">
               🏠
            </a>

            <a href="?page=add"
               class="nav-item {'active' if current_page == 'add' else ''}">
               ➕
            </a>

            <a href="?page=edit"
               class="nav-item {'active' if current_page == 'edit' else ''}">
               ✏️
            </a>

            <a href="?page=budget"
               class="nav-item {'active' if current_page == 'budget' else ''}">
               💰
            </a>

            <a href="?page=analytics"
               class="nav-item {'active' if current_page == 'analytics' else ''}">
               📊
            </a>

        </div>
    </div>
    """,
    unsafe_allow_html=True,
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

    current_month = datetime.now().month
    current_year = datetime.now().year

    current_df = transactions_df[
        (
            transactions_df["date"].dt.month
            == current_month
        )
        &
        (
            transactions_df["date"].dt.year
            == current_year
        )
    ]

    income = current_df[
        current_df["category"] == "income"
    ]["amount"].sum()

    expense = current_df[
        current_df["category"] == "expense"
    ]["amount"].sum()

    saving = income - expense

    total_transactions = len(current_df)

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "💵 Income",
            f"Rp {income:,.0f}",
        )

        st.metric(
            "💸 Expense",
            f"Rp {expense:,.0f}",
        )

    with col2:

        st.metric(
            "🏦 Saving",
            f"Rp {saving:,.0f}",
        )

        st.metric(
            "🧾 Transactions",
            total_transactions,
        )

    st.divider()

    st.subheader("📈 Expense Trend")

    expense_daily = (
        current_df[
            current_df["category"] == "expense"
        ]
        .groupby("date")["amount"]
        .sum()
    )

    st.line_chart(expense_daily)

    st.divider()

    st.subheader("🏦 Account Usage")

    account_usage = account_summary(
        current_df
    )

    st.dataframe(
        account_usage,
        use_container_width=True,
    )

    st.divider()

    st.subheader("🧾 Recent Transactions")

    display_df = current_df.sort_values(
        "date",
        ascending=False,
    )

    st.dataframe(
        display_df,
        use_container_width=True,
    )

# =========================
# ADD TRANSACTION
# =========================

elif page == "Add Transaction":

    st.title("➕ Add Transaction")

    if "add_success" not in st.session_state:
        st.session_state.add_success = False

    if st.session_state.add_success:

        st.success(
            "Transaction added successfully!"
        )

        st.session_state.add_success = False

    with st.form(
        "add_transaction_form",
        clear_on_submit=True,
    ):

        date = st.date_input(
            "Date"
        )

        transaction_name = st.selectbox(
            "Transaction Name",
            transaction_names_df[
                "name"
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

        submitted = st.form_submit_button(
            "Save Transaction"
        )

        if submitted:

            add_transaction(
                {
                    "date": str(date),
                    "name": transaction_name,
                    "category": category,
                    "account": account,
                    "amount": int(amount),
                    "description": description,
                    "created_at": datetime.now().isoformat(),
                }
            )

            st.session_state.add_success = True

            st.rerun()

# =========================
# EDIT TRANSACTION
# =========================

elif page == "Edit Transaction":

    st.title("✏️ Edit Transaction")

    if transactions_df.empty:

        st.warning(
            "No transaction data."
        )

        st.stop()

    transactions_df["label"] = (
        transactions_df["date"]
        .dt.strftime("%Y-%m-%d")
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
            value=selected_row["date"],
        )

        edit_name = st.selectbox(
            "Transaction Name",
            transaction_names_df[
                "name"
            ].tolist(),
            index=transaction_names_df[
                transaction_names_df["name"]
                == selected_row["name"]
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

        account_list = accounts_df[
            "account_name"
        ].tolist()

        current_account = (
            selected_row["account"]
            if "account" in selected_row
            else account_list[0]
        )

        edit_account = st.selectbox(
            "Account",
            account_list,
            index=(
                account_list.index(
                    current_account
                )
                if current_account
                in account_list
                else 0
            ),
        )

        edit_amount = st.number_input(
            "Amount",
            value=int(
                selected_row["amount"]
            ),
            step=1000,
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
                    "category": edit_category,
                    "account": edit_account,
                    "amount": int(edit_amount),
                    "description": edit_description,
                },
            )

            st.success(
                "Transaction updated successfully!"
            )

            st.rerun()

# =========================
# BUDGETING
# =========================

elif page == "Budgeting":

    st.title("🎯 Budgeting")

    st.subheader(
        "Current Budget"
    )

    st.dataframe(
        budget_df,
        use_container_width=True,
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
                "Budget updated successfully!"
            )

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
        "🎯 Budget vs Actual"
    )

    budget_actual = budget_vs_actual(
        transactions_df,
        budget_df,
    )

    st.dataframe(
        budget_actual,
        use_container_width=True,
    )