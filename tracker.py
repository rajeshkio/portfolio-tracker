
from rich.console import Console
import datetime
import utils

dateNow = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
console = Console()
# Load portfolio data from JSON file.
data = utils.load_json("portfolio.json")

# --- Fetch Portfolio ---
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
table = utils.build_pnl_table(results,f"Portfolio Tracker | {dateNow}")

# --- Fetch ETFs ---
etf_portfolio = data["etfs"]
etf_results = []
for r in etf_portfolio:
    try:
        etf_results.append(utils.fetch_stock_data(r["ticker"],r["buy_price"],r["qty"]))
    except Exception as e:
        # If any ticker fails (wrong symbol, delisted, no data), skip it and continue
        print(f"Skipping {r['ticker']}: {e}")
etf_table = utils.build_pnl_table(etf_results,"ETFs")

# --- Fetch Watchlist ---
# Watchlist — stocks we monitor but don't own yet. No P&L columns needed
watchlist = data["watchlist"]
watchlist_results = []
for r in watchlist:
    try:
        watchlist_results.append(utils.fetch_stock_data(r["ticker"]))
    except Exception as e:
        print(f"Skipping {r['ticker']}: {e}")
watchlist_table = utils.build_watchlist_table(watchlist_results,"Watchlist")

# --- Display Tables ---
console.print(table)
console.print(etf_table)
console.print(watchlist_table)

# --- News Prompt ---
utils.show_news_prompt(portfolio,console)