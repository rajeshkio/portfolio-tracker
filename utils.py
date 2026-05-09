import yfinance as yf


def fmt(value):
    return str(round(float(value), 2)) if value is not None else "-"


def fmt_pct(value):
    return f"{value * 100:.2f}%" if value is not None else "-"


def get_pnl_pct(r):
    return r["pnl_pct"]


def clean_ticker(ticker):
    return ticker.replace(".NS", "").replace(".BO", "")


def fetch_stock_data(ticker, buy_price, qty):
    portfolioTicker = yf.Ticker(ticker)
    # period="2d" fetches today and yesterday so we can calculate day change %
    hist = portfolioTicker.history(period="2d").dropna()
    if len(hist) < 2:
        hist = portfolioTicker.history(period="5d").dropna()
    current_price = hist["Close"].iloc[-1]  # iloc[-1] = last row = today
    previous_close = hist["Close"].iloc[-2]  # iloc[-2] = second last row = yesterday
    # Day change % uses previous close, not open — matches what Zerodha/NSE shows
    day_change_pct = ((current_price - previous_close) / previous_close) * 100
    daily_pnl_rs = (current_price - previous_close) * qty
    invested = buy_price * qty
    current_value = current_price * qty
    pnl_rs = current_value - invested
    pnl_pct = (pnl_rs / invested) * 100
    # float() strips numpy's np.float64 wrapper so we get clean Python floats
    return {
        "ticker": ticker,
        "current_price": round(float(current_price), 2),
        "day_change_pct": round(float(day_change_pct), 4),
        "daily_pnl_rs": round(float(daily_pnl_rs), 2),
        "invested": round(invested, 2),
        "pnl_rs": round(float(pnl_rs), 2),
        "pnl_pct": round(float(pnl_pct), 4),
    }
