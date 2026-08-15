import pandas as pd
from services.sheets_client import read_table, get_worksheet, clear_cache, truthy
from utils.ids import next_sequential_id

SHEET = "Accounts"

# Columns: A AccountID | B AccountName | C ParentBucket | D AccountType
# E Owner | F IsActive | G StartingBalance | H CurrentBalance (formula)


def get_accounts() -> pd.DataFrame:
    df = read_table(SHEET)
    if df.empty:
        return df
    df["CurrentBalance"] = pd.to_numeric(df["CurrentBalance"], errors="coerce").fillna(0)
    df["StartingBalance"] = pd.to_numeric(df["StartingBalance"], errors="coerce").fillna(0)
    return df


def get_active_accounts() -> pd.DataFrame:
    df = get_accounts()
    if df.empty:
        return df
    return df[df["IsActive"].apply(truthy)].reset_index(drop=True)


def account_id_lookup(df: pd.DataFrame) -> dict:
    """AccountName -> AccountID, for turning a form's dropdown selection
    back into the key that gets written to Transactions."""
    if df.empty:
        return {}
    return dict(zip(df["AccountName"], df["AccountID"]))


def _current_balance_formula(row: int) -> str:
    """Same formula convention as every other Accounts row: starting balance
    plus/minus everything posted against this account in Transactions,
    excluding voided rows."""
    aid = f"A{row}"
    return (
        f"=G{row}"
        f'+SUMIFS(Transactions!$I:$I,Transactions!$F:$F,{aid},Transactions!$C:$C,"Income",Transactions!$M:$M,FALSE)'
        f'-SUMIFS(Transactions!$I:$I,Transactions!$F:$F,{aid},Transactions!$C:$C,"Expense",Transactions!$M:$M,FALSE)'
        f'-SUMIFS(Transactions!$I:$I,Transactions!$G:$G,{aid},Transactions!$C:$C,"Transfer",Transactions!$M:$M,FALSE)'
        f'+SUMIFS(Transactions!$I:$I,Transactions!$H:$H,{aid},Transactions!$C:$C,"Transfer",Transactions!$M:$M,FALSE)'
    )


def add_account(
    account_name: str,
    parent_bucket: str,
    account_type: str,
    owner: str,
    starting_balance: float = 0,
    is_active: bool = True,
) -> str:
    """Adds a new account with an ID matching the sheet's convention
    (ACC_001, ACC_002, ...) and writes the same CurrentBalance formula every
    other account row uses - so a newly-added account behaves identically
    to the ones that were there from the start, not a special case."""
    ws = get_worksheet(SHEET)
    existing_ids = ws.col_values(1)[1:]  # column A, skip header
    account_id = next_sequential_id(existing_ids, prefix="ACC_", pad=3)
    row_idx = len(existing_ids) + 2

    row = [
        account_id,
        account_name,
        parent_bucket,
        account_type,
        owner,
        is_active,
        starting_balance,
        _current_balance_formula(row_idx),
    ]
    ws.update(f"A{row_idx}:H{row_idx}", [row], value_input_option="USER_ENTERED")
    clear_cache()
    return account_id

