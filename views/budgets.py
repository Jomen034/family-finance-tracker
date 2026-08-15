import streamlit as st

from services.budgets_service import get_budgets_for_month, upsert_budget
from services.categories_service import get_active_subcategories
from utils.dates import current_month_str
from utils.formatting import idr


def render():
    st.title("🎯 Budgets")

    this_month = current_month_str()
    st.caption(f"Editing budgets for **{this_month}** — past months are kept in the Sheet, not overwritten.")

    budgets = get_budgets_for_month(this_month)
    if not budgets.empty:
        display = budgets[["SubCategory", "MonthlyBudget"]].copy()
        display["MonthlyBudget"] = display["MonthlyBudget"].apply(idr)
        st.dataframe(display, use_container_width=True, hide_index=True)
    else:
        st.caption("No budgets set for this month yet.")

    st.divider()

    subcategories = get_active_subcategories()
    if not subcategories:
        st.warning("No active categories found in the Categories sheet.")
        return

    with st.form("budget_form", clear_on_submit=True):
        subcat = st.selectbox("Category", subcategories)
        amount = st.number_input("Monthly Budget (Rp)", min_value=0, step=100000)
        submitted = st.form_submit_button("Save Budget", use_container_width=True, type="primary")
        if submitted:
            upsert_budget(subcat, this_month, amount)
            st.success("Budget saved.")
            st.rerun()
