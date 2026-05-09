import yfinance as yf
import json
from rich.console import Console
from rich.table import Table
import datetime
import utils

dateNow = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")


def show_news(ticker_symbol):
    # Fetch latest news for a given ticker using yfinance's built-in news property
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


# Load portfolio data from JSON file. Keeping data separate from code means
# we never need to edit tracker.py when our holdings change
with open("portfolio.json", "r") as f:
    data = json.load(f)

portfolio = data["portfolio"]
results = []  # will hold calculated results for each stock after fetching

for stock in portfolio:
    try:
        results.append(
            utils.fetch_stock_data(stock["ticker"], stock["buy_price"], stock["qty"])
        )
    except Exception as e:
        # If any ticker fails (wrong symbol, delisted, no data), skip it and continue
        print(f"Skipping {stock['ticker']}: {e}")


results.sort(key=utils.get_pnl_pct, reverse=True)

total_invested = sum(r["invested"] for r in results)
total_pnl_rs = sum(r["pnl_rs"] for r in results)
total_pnl_pct = (total_pnl_rs / total_invested) * 100
total_day_rs = sum(r["daily_pnl_rs"] for r in results)

console = Console()

table = Table(title=f"Portfolio Tracker | {dateNow}")

# justify="right" aligns numbers to the right, standard for financial tables
table.add_column("Stock", style="bold white")
table.add_column("Price (₹)", justify="right")
table.add_column("Last Day %", justify="right")
table.add_column("Last Day (₹)", justify="right")
table.add_column("Invested (₹)", justify="right")
table.add_column("P&L (₹)", justify="right")
table.add_column("P&L %", justify="right")

for r in results:
    pnl_color = "green" if r["pnl_rs"] >= 0 else "red"
    day_color = "green" if r["day_change_pct"] >= 0 else "red"
    # Strip exchange suffixes for clean display — HDFCBANK.NS becomes HDFCBANK
    display_ticker = utils.clean_ticker(r["ticker"])
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
console.print(table)

etf_portfolio = data["etfs"]
etf_results = []
for r in etf_portfolio:
    try:
        etf_results.append(utils.fetch_stock_data(r["ticker"],r["buy_price"],r["qty"]))
    except Exception as e:
        # If any ticker fails (wrong symbol, delisted, no data), skip it and continue
        print(f"Skipping {r['ticker']}: {e}")


etf_results.sort(key=utils.get_pnl_pct, reverse=True)
total_etf_invested = sum(r["invested"] for r in etf_results)
total_etf_pnl_rs = sum(r["pnl_rs"] for r in etf_results)
total_etf_pnl_pct = (total_etf_pnl_rs / total_etf_invested) * 100
total_etf_day_rs = sum(r["daily_pnl_rs"] for r in etf_results)

etf_table = Table(title="ETFs")
# justify="right" aligns numbers to the right, standard for financial tables
etf_table.add_column("Stock", style="bold white")
etf_table.add_column("Price (₹)", justify="right")
etf_table.add_column("Last Day %", justify="right")
etf_table.add_column("Last Day (₹)", justify="right")
etf_table.add_column("Invested (₹)", justify="right")
etf_table.add_column("P&L (₹)", justify="right")
etf_table.add_column("P&L %", justify="right")
for r in etf_results:
    pnl_color = "green" if r["pnl_rs"] >= 0 else "red"
    day_color = "green" if r["day_change_pct"] >= 0 else "red"
    # Strip exchange suffixes for clean display — HDFCBANK.NS becomes HDFCBANK
    display_ticker = r["ticker"].replace(".NS", "").replace(".BO", "")
    # :,.2f formats numbers with thousand separators and 2 decimal places
    price_etf_str = f"{r['current_price']:,.2f}"
    day_etf_str = f"[{day_color}]{r['day_change_pct']:.2f}%[/{day_color}]"
    day_etf_rs_str = f"[{day_color}]{r['daily_pnl_rs']:.2f}[/{day_color}]"
    invested_etf_str = f"{r['invested']:,.2f}"
    pnl_etf_rs_str = f"[{pnl_color}]{r['pnl_rs']:,.2f}[/{pnl_color}]"
    pnl_etf_pct_str = f"[{pnl_color}]{r['pnl_pct']:.2f}%[/{pnl_color}]"

    etf_table.add_row(
        display_ticker,
        price_etf_str,
        day_etf_str,
        day_etf_rs_str,
        invested_etf_str,
        pnl_etf_rs_str,
        pnl_etf_pct_str,
    )

# add_section() draws a separator line above the total row
etf_table.add_section()
total_color = "green" if total_etf_pnl_rs >= 0 else "red"
etf_table.add_row(
    "[bold]TOTAL[/bold]",
    "",
    "",
    f"[bold][{total_color}]{total_day_rs:,.2f}[/{total_color}][/bold]",
    f"[bold]{total_etf_invested:,.2f}[/bold]",
    f"[bold][{total_color}]{total_etf_pnl_rs:,.2f}[/{total_color}][/bold]",
    f"[bold][{total_color}]{total_etf_pnl_pct:.2f}%[/{total_color}][/bold]",
)
console.print(etf_table)


# Watchlist — stocks we monitor but don't own yet. No P&L columns needed
watchlist = data["watchlist"]
watchlist_results = []
for stock in watchlist:
    try:
        wTicker = yf.Ticker(stock["ticker"])
        hist = wTicker.history(period="2d")
        current_price = hist["Close"].iloc[-1]
        previous_close = hist["Close"].iloc[-2]
        day_change_pct = ((current_price - previous_close) / previous_close) * 100
        watchlist_results.append(
            {
                "ticker": stock["ticker"],
                "current_price": round(float(current_price), 2),
                "day_change_pct": round(float(day_change_pct), 4),
            }
        )
    except Exception as e:
        print(f"Skipping {stock['ticker']}: {e}")

watchlist_table = Table(title="Watchlist")
watchlist_table.add_column("Stock", style="bold white")
watchlist_table.add_column("Price (₹)", justify="right")
watchlist_table.add_column("Last Day %", justify="right")

for r in watchlist_results:
    day_color = "green" if r["day_change_pct"] >= 0 else "red"
    display_ticker = r["ticker"].replace(".NS", "").replace(".BO", "")
    watchlist_table.add_row(
        display_ticker,
        f"{r['current_price']:,.2f}",
        f"[{day_color}]{r['day_change_pct']:.2f}%[/{day_color}]",
    )
console.print(watchlist_table)

# Build ticker_map from portfolio for smart suffix handling in news lookup
ticker_map = {
    s["ticker"].replace(".NS", "").replace(".BO", ""): s["ticker"] for s in portfolio
}
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
