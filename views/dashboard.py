import pandas as pd
import plotly.express as px
import streamlit as st

from services.accounts_service import get_accounts
from services.budgets_service import get_budgets_for_month
from services.transactions_service import get_transactions
from utils.dates import current_month_str
from utils.formatting import idr


def render():
    st.title("📊 Main Dashboard")

    tx = get_transactions()
    accounts = get_accounts()
    this_month = current_month_str()

    if tx.empty:
        st.info("No transactions yet. Add your first one from the ➕ Add page.")
        return

    tx_month = tx[tx["TransactionMonth"] == this_month]
    income = tx_month.loc[tx_month["Type"] == "Income", "Amount"].sum()
    expense = tx_month.loc[tx_month["Type"] == "Expense", "Amount"].sum()
    net_worth = accounts["CurrentBalance"].sum() if not accounts.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Net Worth", idr(net_worth))
    c2.metric("📥 Income (this month)", idr(income))
    c3.metric("📤 Expense (this month)", idr(expense))
    c4.metric("📈 Net (this month)", idr(income - expense))

    st.divider()

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Spending by Category")
        expense_rows = tx_month[tx_month["Type"] == "Expense"]
        if not expense_rows.empty:
            by_cat = expense_rows.groupby("SubCategory")["Amount"].sum().reset_index()
            fig = px.pie(by_cat, names="SubCategory", values="Amount", hole=0.45)
            fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.caption("No expenses logged this month yet.")

    with col_b:
        st.subheader("Budget vs Actual")
        budgets = get_budgets_for_month(this_month)
        if budgets.empty:
            st.caption(f"No budget set for {this_month} yet — set one on the 🎯 Budgets page.")
        else:
            expense_rows = tx_month[tx_month["Type"] == "Expense"]
            spend_by_cat = (
                expense_rows.groupby("SubCategory")["Amount"].sum()
                if not expense_rows.empty
                else pd.Series(dtype=float)
            )
            for _, row in budgets.iterrows():
                actual = float(spend_by_cat.get(row["SubCategory"], 0))
                budget_amt = float(row["MonthlyBudget"])
                pct = (actual / budget_amt) if budget_amt else 0
                st.write(f"**{row['SubCategory']}**  \n{idr(actual)} of {idr(budget_amt)}")
                st.progress(min(pct, 1.0))
                if pct >= 1:
                    st.caption("⚠️ Over budget this month")

    st.divider()

    st.subheader("🏦 Account Balances")
    if not accounts.empty:
        display = accounts[["AccountName", "Owner", "ParentBucket", "CurrentBalance"]].copy()
        display["CurrentBalance"] = display["CurrentBalance"].apply(idr)
        display = display.rename(columns={"ParentBucket": "Group"})
        st.dataframe(display, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🕒 Recent Activity")
    recent = tx.sort_values("CreatedAt", ascending=False).head(10).copy()
    recent["Amount"] = recent["Amount"].apply(idr)
    cols = [c for c in ["Date", "Type", "SubCategory", "Amount", "EnteredBy", "Notes"] if c in recent.columns]
    st.dataframe(recent[cols], use_container_width=True, hide_index=True)
