import yfinance as yf
import json
from rich.console import Console
from rich.table import Table

def show_news(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    news = t.news
    if not news:
        print("no news found.")
        return
    print(f"\nTop news for {ticker_symbol}:")
    for item in news[:3]:
        title = item["content"]["title"]
        publisher = item["content"]["provider"]["displayName"]
        url = item["content"]["clickThroughUrl"]["url"]
        print(f"\n  {title}")
        print(f"\n {publisher}")
        print(f" {url}")

with open ("portfolio.json", "r") as f:
    data = json.load(f)

portfolio = data["portfolio"]
results = []

for stock in portfolio:
    try:
        portfolioTicker = yf.Ticker(stock["ticker"])
        hist = portfolioTicker.history(period="2d")
        current_price = hist["Close"].iloc[-1]
        previous_close = hist["Close"].iloc[-2]
        day_change_pct = ((current_price - previous_close) / previous_close) * 100
        invested = stock["buy_price"] * stock["qty"]
        current_value = current_price * stock["qty"]
        pnl_rs = current_value - invested
        pnl_pct = (pnl_rs/invested) * 100
        results.append({
            "ticker": stock["ticker"],
            "current_price":round(float(current_price),2),
            "day_change_pct":round(float(day_change_pct),4),
            "invested":round(invested,2),
            "pnl_rs":round(float(pnl_rs),2),
            "pnl_pct":round(float(pnl_pct),4)
            })
    except Exception as e:
        print(f"Skipping {stock['ticker']}: {e}")

total_invested = sum(r["invested"] for r in results)
total_pnl_rs = sum(r["pnl_rs"] for r in results)
total_pnl_pct = (total_pnl_rs/total_invested) * 100

console = Console()

table = Table(title="Portfolio Tracker")


table.add_column("Stock", style="bold white")
table.add_column("Price (₹)", justify="right")
table.add_column("Day %", justify="right")
table.add_column("Invested (₹)", justify="right")
table.add_column("P&L (₹)", justify="right")
table.add_column("P&L %", justify="right")

for r in results:
    pnl_color = "green" if r["pnl_rs"] >= 0 else "red"
    day_color = "green" if r["day_change_pct"] >= 0 else "red"
    display_ticker = r["ticker"].replace(".NS", "").replace(".BO", "")
    price_str = f"{r['current_price']:,.2f}"
    day_str = f"[{day_color}]{r['day_change_pct']:.2f}%[/{day_color}]"
    invested_str = f"{r['invested']:,.2f}"
    pnl_rs_str = f"[{pnl_color}]{r['pnl_rs']:,.2f}[/{pnl_color}]"
    pnl_pct_str = f"[{pnl_color}]{r['pnl_pct']:.2f}%[/{pnl_color}]"

    table.add_row(
    display_ticker,
    price_str,
    day_str,
    invested_str,
    pnl_rs_str,
    pnl_pct_str,
)
table.add_section()
total_color = "green" if total_pnl_rs >= 0 else "red"
table.add_row(
    "[bold]TOTAL[/bold]",
    "",
    "",
    f"[bold]{total_invested:,.2f}[/bold]",
    f"[bold][{total_color}]{total_pnl_rs:,.2f}[/{total_color}][/bold]",
    f"[bold][{total_color}]{total_pnl_pct:.2f}%[/{total_color}][/bold]"
)

console.print(table)

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
            ticker_input = ticker_input + ".NS"
        show_news(ticker_input)
except KeyboardInterrupt:
    console.print("\n[bold yellow]Exiting...[/bold yellow]")