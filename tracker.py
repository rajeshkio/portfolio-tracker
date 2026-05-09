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

console = Console()

table = utils.build_pnl_table(results,f"Portfolio Tracker | {dateNow}")
console.print(table)

etf_portfolio = data["etfs"]
etf_results = []
for r in etf_portfolio:
    try:
        etf_results.append(utils.fetch_stock_data(r["ticker"],r["buy_price"],r["qty"]))
    except Exception as e:
        # If any ticker fails (wrong symbol, delisted, no data), skip it and continue
        print(f"Skipping {r['ticker']}: {e}")



etf_table = utils.build_pnl_table(etf_results,"ETFs")
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
