from datetime import date


def current_month_str() -> str:
    """Returns the current month as YYYY-MM, matching the format used by
    Transactions.TransactionMonth and Budgets.EffectiveMonth in the Sheet."""
    return date.today().strftime("%Y-%m")
