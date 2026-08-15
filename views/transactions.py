import streamlit as st

from services.transactions_service import get_transactions, void_transaction
from utils.formatting import idr


def render():
    st.title("🧾 Transactions")

    tx = get_transactions()
    if tx.empty:
        st.info("No transactions yet.")
        return

    tx = tx.sort_values("Date", ascending=False)

    for _, row in tx.iterrows():
        label_bits = [str(row.get("Date", "")), row.get("Type", ""), idr(row.get("Amount", 0))]
        notes = row.get("Notes", "")
        if notes:
            label_bits.append(notes)
        label = " · ".join(str(b) for b in label_bits if b)

        with st.expander(label):
            category = row.get("SubCategory") or "-"
            st.write(f"**Category:** {category}")
            st.write(f"**Entered by:** {row.get('EnteredBy') or '-'}")
            if row.get("Type") == "Transfer":
                st.write(f"**From:** {row.get('FromAccountID')}  →  **To:** {row.get('ToAccountID')}")
            else:
                st.write(f"**Account:** {row.get('AccountID')}")

            if st.button("🗑️ Void this transaction", key=f"void_{row['TransactionID']}"):
                void_transaction(row["TransactionID"])
                st.success("Transaction voided.")
                st.rerun()
