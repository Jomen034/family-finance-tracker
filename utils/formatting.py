def idr(amount) -> str:
    """Formats a number as Indonesian Rupiah: Rp 1.234.567 (dot thousands
    separator, no decimals - matches how the family actually reads money)."""
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        amount = 0
    formatted = f"{amount:,.0f}".replace(",", ".")
    return f"Rp {formatted}"
