import yfinance as yf
import json
from rich.console import Console
from rich.table import Table
import datetime

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
with open ("portfolio.json", "r") as f:
    data = json.load(f)

portfolio = data["portfolio"]
results = [] # will hold calculated results for each stock after fetching

for stock in portfolio:
    try:
        portfolioTicker = yf.Ticker(stock["ticker"])
        # period="2d" fetches today and yesterday so we can calculate day change %
        hist = portfolioTicker.history(period="2d")
        current_price = hist["Close"].iloc[-1]         # iloc[-1] = last row = today
        previous_close = hist["Close"].iloc[-2]        # iloc[-2] = second last row = yesterday
        # Day change % uses previous close, not open — matches what Zerodha/NSE shows
        day_change_pct = ((current_price - previous_close) / previous_close) * 100
        daily_pnl_rs = (current_price - previous_close) * stock["qty"]
        invested = stock["buy_price"] * stock["qty"]
        current_value = current_price * stock["qty"]
        pnl_rs = current_value - invested
        pnl_pct = (pnl_rs/invested) * 100
        # float() strips numpy's np.float64 wrapper so we get clean Python floats
        results.append({
            "ticker": stock["ticker"],
            "current_price":round(float(current_price),2),
            "day_change_pct":round(float(day_change_pct),4),
            "daily_pnl_rs" :round(float(daily_pnl_rs),2),
            "invested":round(invested,2),
            "pnl_rs":round(float(pnl_rs),2),
            "pnl_pct":round(float(pnl_pct),4)
            })
    except Exception as e:
        # If any ticker fails (wrong symbol, delisted, no data), skip it and continue
        print(f"Skipping {stock['ticker']}: {e}")

def get_pnl_pct(r):
    return r["pnl_pct"]
results.sort(key=get_pnl_pct, reverse=True)

total_invested = sum(r["invested"] for r in results)
total_pnl_rs = sum(r["pnl_rs"] for r in results)
total_pnl_pct = (total_pnl_rs/total_invested) * 100
total_day_rs = sum(r["daily_pnl_rs"] for r in results)

console = Console()

table = Table(title=f"Portfolio Tracker | {dateNow}")

# justify="right" aligns numbers to the right, standard for financial tables
table.add_column("Stock", style="bold white")
table.add_column("Price (₹)", justify="right")
table.add_column("Day %", justify="right")
table.add_column("Day (₹)", justify="right")
table.add_column("Invested (₹)", justify="right")
table.add_column("P&L (₹)", justify="right")
table.add_column("P&L %", justify="right")

for r in results:
    pnl_color = "green" if r["pnl_rs"] >= 0 else "red"
    day_color = "green" if r["day_change_pct"] >= 0 else "red"
    # Strip exchange suffixes for clean display — HDFCBANK.NS becomes HDFCBANK
    display_ticker = r["ticker"].replace(".NS", "").replace(".BO", "")
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
    f"[bold][{total_color}]{total_pnl_pct:.2f}%[/{total_color}][/bold]"
)
console.print(table)

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
        watchlist_results.append({
            "ticker": stock["ticker"],
            "current_price": round(float(current_price), 2),
            "day_change_pct": round(float(day_change_pct), 4)
        })
    except Exception as e:
        print(f"Skipping {stock['ticker']}: {e}")

watchlist_table =  Table(title="Watchlist")
watchlist_table.add_column("Stock", style="bold white")
watchlist_table.add_column("Price (₹)", justify="right")
watchlist_table.add_column("Day %", justify="right")

for r in watchlist_results:
    day_color = "green" if r["day_change_pct"] >= 0 else "red"
    display_ticker = r["ticker"].replace(".NS","").replace(".BO","")
    watchlist_table.add_row(
        display_ticker,
        f"{r['current_price']:,.2f}",
        f"[{day_color}]{r['day_change_pct']:.2f}%[/{day_color}]"
    )
console.print(watchlist_table)

# Build ticker_map from portfolio for smart suffix handling in news lookup
ticker_map = {s["ticker"].replace(".NS", "").replace(".BO", ""): s["ticker"] for s in portfolio}
valid_tickers = list(ticker_map.keys())
console.print(f"\n[bold]Available tickers:[/bold] {', '.join(valid_tickers)}")

try:
    while True:
        ticker_input = input("\nEnter ticker for news (or Enter to skip): ").strip().upper()
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

