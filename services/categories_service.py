from services.sheets_client import read_table, get_worksheet, clear_cache, truthy
from utils.ids import next_sequential_id

SHEET = "Categories"

# Columns: A CategoryID | B MainCategory | C SubCategory | D GroupType | E IsActive
# SubCategory is the real join key used by Transactions/Budgets, so it must
# stay unique - add_category() enforces that.


def get_categories():
    return read_table(SHEET)


def get_active_subcategories() -> list:
    df = get_categories()
    if df.empty:
        return []
    active = df[df["IsActive"].apply(truthy)]
    return sorted(active["SubCategory"].dropna().unique().tolist())


def add_category(main_category: str, subcategory: str, group_type: str, is_active: bool = True) -> str:
    """Adds a new category with an ID matching the sheet's convention
    (CAT_001, CAT_002, ...). Refuses to add a SubCategory that already
    exists (case-insensitive) since Transactions and Budgets both join to
    it by name - a duplicate would silently split one category's data
    across two rows."""
    ws = get_worksheet(SHEET)
    existing_ids = ws.col_values(1)[1:]  # column A, skip header
    existing_subcats = [s.strip().lower() for s in ws.col_values(3)[1:]]  # column C

    if subcategory.strip().lower() in existing_subcats:
        raise ValueError(f'"{subcategory}" already exists as a category - pick a different name.')

    category_id = next_sequential_id(existing_ids, prefix="CAT_", pad=3)
    row_idx = len(existing_ids) + 2

    row = [category_id, main_category, subcategory.strip(), group_type, is_active]
    ws.update(f"A{row_idx}:E{row_idx}", [row], value_input_option="USER_ENTERED")
    clear_cache()
    return category_id
