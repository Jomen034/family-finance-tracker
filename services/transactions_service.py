from datetime import datetime
from typing import Optional

import pandas as pd

from services.sheets_client import (
    read_table,
    get_worksheet,
    clear_cache,
    find_row_by_id,
    truthy,
)
from utils.ids import next_sequential_id

SHEET = "Transactions"

# Column layout on the Transactions tab (1-indexed, matches the V5.1 schema):
# A TransactionID | B Date | C Type | D MainCategory (formula) | E SubCategory
# F AccountID | G FromAccountID | H ToAccountID | I Amount | J Notes
# K EnteredBy | L CreatedAt | M IsVoided | N TransactionMonth (formula)
COL_IS_VOIDED = 13


def _main_category_formula(row: int) -> str:
    return f'=IFERROR(INDEX(Categories!$B:$B,MATCH(E{row},Categories!$C:$C,0)),"")'


def _month_formula(row: int) -> str:
    return f'=IF(B{row}="","",TEXT(B{row},"YYYY-MM"))'


def get_all_transactions() -> pd.DataFrame:
    """Raw read, voided rows included - used for audit views."""
    df = read_table(SHEET)
    if df.empty:
        return df
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    return df


def get_transactions() -> pd.DataFrame:
    """Active (non-voided) transactions - what the dashboard and lists use."""
    df = get_all_transactions()
    if df.empty:
        return df
    return df[~df["IsVoided"].apply(truthy)].reset_index(drop=True)


def add_transaction(
    date,
    ttype: str,
    subcategory: Optional[str],
    account_id: Optional[str],
    from_account_id: Optional[str],
    to_account_id: Optional[str],
    amount: float,
    notes: str,
    entered_by: str,
) -> str:
    """Writes a full row (A:N) so the MainCategory/TransactionMonth formulas
    are (re)written explicitly on every insert - this keeps the sheet correct
    forever, instead of relying on formulas being pre-dragged down in advance.

    TransactionID is generated to match the sheet's existing convention
    (TRX_1001, TRX_1002, ...) by reading the current max and incrementing -
    never a random/UUID-style ID that would look inconsistent next to the
    original rows."""
    ws = get_worksheet(SHEET)
    existing_ids = ws.col_values(1)[1:]  # column A, skip header
    trx_id = next_sequential_id(existing_ids, prefix="TRX_", pad=4, start=1001)
    row_idx = len(existing_ids) + 2  # header row + existing rows + this new one

    row = [
        trx_id,
        str(date),
        ttype,
        _main_category_formula(row_idx),
        subcategory or "",
        account_id or "",
        from_account_id or "",
        to_account_id or "",
        amount,
        notes or "",
        entered_by or "",
        datetime.now().isoformat(timespec="seconds"),
        False,
        _month_formula(row_idx),
    ]
    ws.update(f"A{row_idx}:N{row_idx}", [row], value_input_option="USER_ENTERED")
    clear_cache()
    return trx_id


def void_transaction(transaction_id: str) -> bool:
    """Soft-delete: flips IsVoided to TRUE. Never deletes the row, so the
    audit trail and account balances stay correct and reversible."""
    row_idx = find_row_by_id(SHEET, "TransactionID", transaction_id)
    if row_idx is None:
        return False
    ws = get_worksheet(SHEET)
    ws.update_cell(row_idx, COL_IS_VOIDED, True)
    clear_cache()
    return True
