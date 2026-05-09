import yfinance as yf
import json
from rich.console import Console
from rich.table import Table
import datetime
import utils

dateNow = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

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
for r in watchlist:
    try:
        watchlist_results.append(utils.fetch_stock_data(r["ticker"]))
    except Exception as e:
        print(f"Skipping {r['ticker']}: {e}")

watchlist_table = utils.build_watchlist_table(watchlist_results,"Watchlist")
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
        utils.show_news(ticker_input)
except KeyboardInterrupt:
    console.print("\n[bold yellow]Exiting...[/bold yellow]")
