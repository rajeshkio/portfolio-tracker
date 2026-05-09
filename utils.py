import yfinance as yf
import json
from rich.console import Console
from rich.table import Table


def fmt(value):
    """Format a number to 2 decimal places, returns '-' if None."""
    return str(round(float(value), 2)) if value is not None else "-"


def fmt_pct(value):
    """Format percentage to 2 decimal places, returns '-' if None."""
    return f"{value * 100:.2f}%" if value is not None else "-"


def get_pnl_pct(r):
    """Return pnl_pct value from a result dictionary, used as a sort key"""
    return r["pnl_pct"]


def load_json(filename):
    """Load filename in json"""
    with open(filename, "r") as f:
        data = json.load(f)
    return data


def save_json(filename, data):
    """Write json data to a filename"""
    with open(filename, "w") as f:
        json.dump(data, f)


def clean_ticker(ticker):
    """Remove .NS and .BO from ticker to list properly in the table"""
    return ticker.replace(".NS", "").replace(".BO", "")


def fetch_stock_data(ticker, buy_price=None, qty=None):
    """Fetch portfolio stocks and calculate profit and loss"""
    portfolioTicker = yf.Ticker(ticker)
    # period="2d" fetches today and yesterday so we can calculate day change %
    hist = portfolioTicker.history(period="2d").dropna()

    if len(hist) < 2:
        hist = portfolioTicker.history(period="5d").dropna()

    current_price = hist["Close"].iloc[-1]  # iloc[-1] = last row = today
    previous_close = hist["Close"].iloc[-2]  # iloc[-2] = second last row = yesterday
    # Day change % uses previous close, not open — matches what Zerodha/NSE shows
    day_change_pct = ((current_price - previous_close) / previous_close) * 100
    if qty is not None:
        daily_pnl_rs = (current_price - previous_close) * qty
        invested = buy_price * qty
        current_value = current_price * qty
        pnl_rs = current_value - invested
        pnl_pct = (pnl_rs / invested) * 100
    # float() strips numpy's np.float64 wrapper so we get clean Python floats
    result = {
        "ticker": ticker,
        "current_price": round(float(current_price), 2),
        "day_change_pct": round(float(day_change_pct), 4),
    }
    if qty is not None and buy_price is not None:
        result["daily_pnl_rs"] = round(float(daily_pnl_rs), 2)
        result["invested"] = round(invested, 2)
        result["pnl_rs"] = round(float(pnl_rs), 2)
        result["pnl_pct"] = round(float(pnl_pct), 4)
    return result


def build_pnl_table(results, title):
    """Build and beautify portfolio stocks in a table"""
    table = Table(title=title)
    table.add_column("Stock", style="bold white")
    table.add_column("Price (₹)", justify="right")
    table.add_column("Last Day %", justify="right")
    table.add_column("Last Day (₹)", justify="right")
    table.add_column("Invested (₹)", justify="right")
    table.add_column("P&L (₹)", justify="right")
    table.add_column("P&L %", justify="right")
    results.sort(key=get_pnl_pct, reverse=True)
    for r in results:
        pnl_color = "green" if r["pnl_rs"] >= 0 else "red"
        day_color = "green" if r["day_change_pct"] >= 0 else "red"
        # Strip exchange suffixes for clean display — HDFCBANK.NS becomes HDFCBANK
        display_ticker = clean_ticker(r["ticker"])
        # :,.2f formats numbers with thousand separators and 2 decimal places
        price_str = f"{r['current_price']:,.2f}"
        day_str = f"[{day_color}]{r['day_change_pct']:.2f}%[/{day_color}]"
        day_rs_str = f"[{day_color}]{r['daily_pnl_rs']:.2f}[/{day_color}]"
        invested_str = f"{r['invested']:,.2f}"
        pnl_rs_str = f"[{pnl_color}]{r['pnl_rs']:,.2f}[/{pnl_color}]"
        pnl_pct_str = f"[{pnl_color}]{r['pnl_pct']:.2f}%[/{pnl_color}]"

        table.add_row(
            display_ticker,
            price_str,
            day_str,
            day_rs_str,
            invested_str,
            pnl_rs_str,
            pnl_pct_str,
        )

    total_invested = sum(r["invested"] for r in results)
    total_pnl_rs = sum(r["pnl_rs"] for r in results)
    total_pnl_pct = (total_pnl_rs / total_invested) * 100
    total_day_rs = sum(r["daily_pnl_rs"] for r in results)

    # add_section() draws a separator line above the total row
    table.add_section()
    total_color = "green" if total_pnl_rs >= 0 else "red"
    table.add_row(
        "[bold]TOTAL[/bold]",
        "",
        "",
        f"[bold][{total_color}]{total_day_rs:,.2f}[/{total_color}][/bold]",
        f"[bold]{total_invested:,.2f}[/bold]",
        f"[bold][{total_color}]{total_pnl_rs:,.2f}[/{total_color}][/bold]",
        f"[bold][{total_color}]{total_pnl_pct:.2f}%[/{total_color}][/bold]",
    )
    return table


def build_watchlist_table(results, title):
    """Build and beautify watchlist stocks in a table"""
    table = Table(title=title)
    table.add_column("Stock", style="bold white")
    table.add_column("Price (₹)", justify="right")
    table.add_column("Last Day %", justify="right")

    for r in results:
        day_color = "green" if r["day_change_pct"] >= 0 else "red"
        display_ticker = clean_ticker(r["ticker"])
        table.add_row(
            display_ticker,
            f"{r['current_price']:,.2f}",
            f"[{day_color}]{r['day_change_pct']:.2f}%[/{day_color}]",
        )
    return table


def show_news(ticker_symbol):
    """Fetch latest news for a given ticker using yfinance's built-in news property"""
    t = yf.Ticker(ticker_symbol)
    news = t.news
    if not news:
        print("no news found.")
        return
    print(f"\nTop news for {ticker_symbol}:")
    # Show only top 3 headlines. news[:3] slices the first 3 items from the list
    for item in news[:3]:
        # News data is deeply nested. Title and URL are inside content -> clickThroughUrl
        title = item["content"]["title"]
        publisher = item["content"]["provider"]["displayName"]
        url = item["content"]["clickThroughUrl"]["url"]
        print(f"\n  {title}")
        print(f"\n {publisher}")
        print(f" {url}")


def show_news_prompt(portfolio, console):
    """Give prompt for the user to get a news for portfolio stocks"""
    ticker_map = {clean_ticker(s["ticker"]): s["ticker"] for s in portfolio}
    valid_tickers = list(ticker_map.keys())
    console.print(f"\n[bold]Available tickers:[/bold] {', '.join(valid_tickers)}")
    try:
        while True:
            ticker_input = (
                input("\nEnter ticker for news (or Enter to skip): ").strip().upper()
            )
            if not ticker_input:
                break
            if ticker_input in ticker_map:
                ticker_input = ticker_map[ticker_input]
            elif ticker_input != "MSFT":
                # Default to .NS for any Indian stock not in portfolio
                ticker_input = ticker_input + ".NS"
            show_news(ticker_input)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Exiting...[/bold yellow]")


def fetch_fundamentals(ticker, dateNow):
    """Fetch fundamental numbers for the portfolio stocks"""
    t = yf.Ticker(ticker)
    return {
        "ticker": ticker,
        "trailingPE": t.info.get("trailingPE", None),
        "forwardPE": t.info.get("forwardPE", None),
        "trailingEps": t.info.get("trailingEps", None),
        "earningsGrowth": t.info.get("earningsGrowth", None),
        "returnOnEquity": t.info.get("returnOnEquity", None),
        "profitMargins": t.info.get("profitMargins", None),
        "targetMeanPrice": t.info.get("targetMeanPrice", None),
        "recommendationKey": t.info.get("recommendationKey", None),
        "lastUpdated": dateNow,
    }


def build_fundamentals_table(data, title, dateNow):
    """Build and beautify fundamentals into a table"""
    table = Table(title=f"{title} | {dateNow}")
    # justify="right" aligns numbers to the right, standard for financial tables
    table.add_column("Stock", style="bold white")
    table.add_column("P/E", justify="right")
    table.add_column("Forward P/E", justify="right")
    table.add_column("EPS", justify="right")
    table.add_column("Earnings Growth", justify="right")
    table.add_column("ROE", justify="right")
    table.add_column("Profit Margin", justify="right")
    table.add_column("Analyst Target", justify="right")
    table.add_column("Recommendation", justify="right")
    table.add_column("Last Updated", justify="right")

    for r in data:
        if r["recommendationKey"] == "strong_buy" or r["recommendationKey"] == "buy":
            recommend_color = "green"
        elif r["recommendationKey"] == "hold":
            recommend_color = "yellow"
        else:
            recommend_color = "white"
        display_ticker = clean_ticker(r["ticker"])
        pe_str = fmt(r["trailingPE"])
        forward_pe = fmt(r["forwardPE"])
        eps_str = fmt(r["trailingEps"])
        earning_growth = fmt_pct(r["earningsGrowth"])
        return_on_equity = fmt_pct(r["returnOnEquity"])
        profit_margin = fmt_pct(r["profitMargins"])
        target_mean_price = fmt(r["targetMeanPrice"])
        recommendation = f"[{recommend_color}]{str(r['recommendationKey']).replace('_', ' ').title()}[/{recommend_color}]"
        last_updated = r["lastUpdated"]

        table.add_row(
            display_ticker,
            str(pe_str),
            str(forward_pe),
            str(eps_str),
            str(earning_growth),
            str(return_on_equity),
            str(profit_margin),
            str(target_mean_price),
            recommendation,
            last_updated,
        )
    return table
