from datetime import date

import streamlit as st

from services.accounts_service import get_active_accounts, account_id_lookup
from services.categories_service import get_active_subcategories
from services.transactions_service import add_transaction


def render():
    st.title("➕ Add Transaction")

    accounts_df = get_active_accounts()
    account_names = accounts_df["AccountName"].tolist() if not accounts_df.empty else []
    ids_by_name = account_id_lookup(accounts_df)
    subcategories = get_active_subcategories()

    if not account_names:
        st.warning("No active accounts found in the Accounts sheet.")
        return
    if not subcategories:
        st.warning("No active categories found in the Categories sheet.")
        return

    entered_by = st.session_state.get("entered_by", "Suami")

    # Type sits outside the form so the rest of the form can adapt to it
    # immediately - this is what keeps the input to only the fields that matter.
    ttype = st.selectbox("Type", ["Expense", "Income", "Transfer"])

    with st.form("add_transaction_form", clear_on_submit=True):
        trx_date = st.date_input("Date", value=date.today())

        subcategory = account_name = from_name = to_name = None

        if ttype in ("Expense", "Income"):
            subcategory = st.selectbox("Category", subcategories)
            account_name = st.selectbox("Account", account_names)
        else:
            from_name = st.selectbox("From Account", account_names)
            to_name = st.selectbox("To Account", account_names)

        amount = st.number_input("Amount (Rp)", min_value=0, step=1000)
        notes = st.text_input("Notes")

        submitted = st.form_submit_button("Save Transaction", use_container_width=True, type="primary")

        if submitted:
            if amount <= 0:
                st.error("Amount must be greater than 0.")
            elif ttype == "Transfer" and from_name == to_name:
                st.error("From and To accounts can't be the same.")
            else:
                add_transaction(
                    date=trx_date,
                    ttype=ttype,
                    subcategory=subcategory,
                    account_id=ids_by_name.get(account_name),
                    from_account_id=ids_by_name.get(from_name),
                    to_account_id=ids_by_name.get(to_name),
                    amount=amount,
                    notes=notes,
                    entered_by=entered_by,
                )
                st.success("Transaction saved!")
                st.rerun()
