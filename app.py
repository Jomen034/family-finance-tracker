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
# SESSION
# =========================

if "entered_app" not in st.session_state:
    st.session_state.entered_app = False

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

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
        gap: 0.4rem;
    }

    .stButton > button {
        border-radius: 18px;
    }

    /* MOBILE NAVIGATION */

    .bottom-nav-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;

        background-color: #0B1120;

        padding-top: 10px;
        padding-bottom: 16px;
        padding-left: 10px;
        padding-right: 10px;

        border-top: 1px solid #1F2937;

        z-index: 999999;
    }

    .bottom-space {
        height: 90px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# WELCOME SCREEN
# =========================

if not st.session_state.entered_app:

    st.markdown(
        """
        <div style="
            text-align:center;
            padding-top:90px;
            padding-bottom:40px;
        ">

            <h1 style="
                font-size:72px;
                margin-bottom:10px;
            ">
                💰
            </h1>

            <h1 style="
                font-size:54px;
                margin-bottom:0;
                line-height:1.1;
            ">
                GFams
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

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

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

selected_tab = st.session_state.page

st.markdown(
    '<div class="bottom-nav-container">',
    unsafe_allow_html=True,
)

nav1, nav2, nav3, nav4, nav5 = st.columns(5)

with nav1:

    if st.button(
        "🏠",
        use_container_width=True,
    ):
        st.session_state.page = "dashboard"
        st.rerun()

with nav2:

    if st.button(
        "➕",
        use_container_width=True,
    ):
        st.session_state.page = "add"
        st.rerun()

with nav3:

    if st.button(
        "✏️",
        use_container_width=True,
    ):
        st.session_state.page = "edit"
        st.rerun()

with nav4:

    if st.button(
        "💰",
        use_container_width=True,
    ):
        st.session_state.page = "budget"
        st.rerun()

with nav5:

    if st.button(
        "📊",
        use_container_width=True,
    ):
        st.session_state.page = "analytics"
        st.rerun()

st.markdown(
    "</div>",
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

# =========================
# BOTTOM SPACE
# =========================

st.markdown(
    '<div class="bottom-space"></div>',
    unsafe_allow_html=True,
)