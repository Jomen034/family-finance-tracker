import streamlit as st

from services.accounts_service import get_accounts, add_account
from services.categories_service import get_categories, add_category


def render():
    st.title("⚙️ Manage Accounts & Categories")
    st.caption("Setup data — added once, rarely changed. Everyone shares the same list.")

    tab_accounts, tab_categories = st.tabs(["🏦 Accounts", "🏷️ Categories"])

    with tab_accounts:
        _render_accounts()

    with tab_categories:
        _render_categories()


def _render_accounts():
    accounts = get_accounts()
    if not accounts.empty:
        display = accounts[["AccountID", "AccountName", "ParentBucket", "AccountType", "Owner", "IsActive"]].copy()
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.caption("No accounts yet.")

    st.divider()
    st.subheader("Add Account")
    with st.form("add_account_form", clear_on_submit=True):
        name = st.text_input("Account Name", placeholder="e.g. Suami - Debit Mandiri")
        parent_bucket = st.text_input("Group Label", placeholder="e.g. 1. Operating & Salary")
        account_type = st.selectbox("Account Type", ["Asset", "Liability"])
        owner = st.selectbox("Owner", ["Suami", "Istri", "Bersama"])
        starting_balance = st.number_input("Starting Balance (Rp)", value=0, step=1000)
        submitted = st.form_submit_button("Add Account", use_container_width=True, type="primary")

        if submitted:
            if not name.strip() or not parent_bucket.strip():
                st.error("Account Name and Group Label are required.")
            else:
                new_id = add_account(
                    account_name=name.strip(),
                    parent_bucket=parent_bucket.strip(),
                    account_type=account_type,
                    owner=owner,
                    starting_balance=starting_balance,
                )
                st.success(f"Added {new_id} — {name}")
                st.rerun()


def _render_categories():
    categories = get_categories()
    if not categories.empty:
        display = categories[["CategoryID", "MainCategory", "SubCategory", "GroupType", "IsActive"]].copy()
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.caption("No categories yet.")

    st.divider()
    st.subheader("Add Category")
    with st.form("add_category_form", clear_on_submit=True):
        main_category = st.selectbox("Main Category", ["Needs", "Wants", "Goals", "Income"])
        subcategory = st.text_input("Sub Category", placeholder="e.g. Wants - Hobbies")
        group_type = st.selectbox("Group Type", ["Expense", "Income", "Savings"])
        submitted = st.form_submit_button("Add Category", use_container_width=True, type="primary")

        if submitted:
            if not subcategory.strip():
                st.error("Sub Category is required.")
            else:
                try:
                    new_id = add_category(main_category, subcategory, group_type)
                    st.success(f"Added {new_id} — {subcategory}")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
