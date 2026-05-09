def fmt(value):
    return str(round(float(value), 2)) if value is not None else "-"

def fmt_pct(value):
    return f"{value * 100:.2f}%" if value is not None else "-"

def get_pnl_pct(r):
    return r["pnl_pct"]

def clean_ticker(ticker):
    return ticker.replace(".NS", "").replace(".BO", "")