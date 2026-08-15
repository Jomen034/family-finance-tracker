import streamlit as st
from streamlit_option_menu import option_menu

from utils.auth import require_login, select_user
from views import dashboard, add_transaction, transactions, budgets, manage

st.set_page_config(page_title="Gaudete Fams Finance Tracker", page_icon="💰", layout="wide")

require_login()
select_user()

with st.sidebar:
    st.caption(f"Logged as **{st.session_state['entered_by']}**")
    if st.button("Switch user"):
        del st.session_state["entered_by"]
        st.rerun()

page = option_menu(
    menu_title=None,
    options=["Dashboard", "Add", "Transactions", "Budgets", "Manage"],
    icons=["house", "plus-circle", "list-ul", "wallet2", "gear"],
    orientation="horizontal",
    default_index=0,
)

if page == "Dashboard":
    dashboard.render()
elif page == "Add":
    add_transaction.render()
elif page == "Transactions":
    transactions.render()
elif page == "Budgets":
    budgets.render()
elif page == "Manage":
    manage.render()
