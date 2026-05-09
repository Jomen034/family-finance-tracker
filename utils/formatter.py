# utils/formatter.py

def format_rupiah(amount):

    try:
        amount = float(amount)
    except:
        amount = 0

    return (
        f"Rp {amount:,.0f}"
        .replace(",", ".")
    )