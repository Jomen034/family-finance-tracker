import pandas as pd

from services.sheets_client import read_table, get_worksheet, clear_cache, next_empty_row
from utils.ids import next_sequential_id

SHEET = "Budgets"


def get_budgets() -> pd.DataFrame:
    df = read_table(SHEET)
    if df.empty:
        return df
    df["MonthlyBudget"] = pd.to_numeric(df["MonthlyBudget"], errors="coerce").fillna(0)
    return df


def get_budgets_for_month(month_str: str) -> pd.DataFrame:
    df = get_budgets()
    if df.empty:
        return df
    return df[df["EffectiveMonth"] == month_str].reset_index(drop=True)


def upsert_budget(subcategory: str, month_str: str, amount: float) -> None:
    """Updates the existing budget row for this SubCategory+Month if one
    exists, otherwise appends a new one. Never overwrites a different month,
    so budget history for past months stays intact.

    New BudgetIDs are scoped to the month (BDG_202608_001, BDG_202608_002, ...)
    matching the sheet's existing convention - numbering restarts cleanly for
    each new month rather than just following the sheet's absolute row count,
    which would produce IDs like BDG_202609_047 the moment budgets from
    different months are interleaved."""
    ws = get_worksheet(SHEET)
    df = get_budgets()

    existing = pd.DataFrame()
    if not df.empty:
        existing = df[(df["SubCategory"] == subcategory) & (df["EffectiveMonth"] == month_str)]

    if not existing.empty:
        sheet_row = existing.index[0] + 2  # +1 header, +1 to move from 0-index to 1-index
        ws.update(f"D{sheet_row}", [[amount]], value_input_option="USER_ENTERED")
    else:
        month_prefix = f"BDG_{month_str.replace('-', '')}_"
        existing_ids_this_month = (
            df[df["BudgetID"].str.startswith(month_prefix)]["BudgetID"].tolist()
            if not df.empty
            else []
        )
        budget_id = next_sequential_id(existing_ids_this_month, prefix=month_prefix, pad=3)
        row_idx = next_empty_row(SHEET)
        ws.update(
            f"A{row_idx}:D{row_idx}",
            [[budget_id, subcategory, month_str, amount]],
            value_input_option="USER_ENTERED",
        )
    clear_cache()
