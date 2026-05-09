import yfinance as yf
import json
import datetime
from rich.console import Console
from rich.table import Table
import utils


# converting to string as type datetime is not JSON serializable
dateNow = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
fundamentals = []

with open("portfolio.json", "r") as f:
    data = json.load(f)
portfolio = data["portfolio"]

for stock in portfolio:
    try:
        t = yf.Ticker(stock["ticker"])
        fundamentals.append(
            {
                "ticker": stock["ticker"],
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
        )
    except Exception as e:
        print(f"Skipping {stock['ticker']}: {e}")

#print(fundamentals)

with open("fundamentals.json", "w") as f:
    json.dump(fundamentals, f)


table = Table(title=f"Portfolio Tracker | {dateNow}")
console = Console()

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

with open("fundamentals.json", "r") as f:
    data = json.load(f)

for r in data:
    if r["recommendationKey"] == "strong_buy" or r["recommendationKey"] == "buy":
        recommend_color = "green"
    elif r["recommendationKey"] == "hold":
        recommend_color = "yellow"
    else:
        recommend_color = "white"
    display_ticker = r["ticker"].replace(".NS", "").replace(".BO", "")
    pe_str = utils.fmt(r["trailingPE"])
    forward_pe = utils.fmt(r["forwardPE"])
    eps_str = utils.fmt(r["trailingEps"])
    earning_growth = utils.fmt_pct(r["earningsGrowth"])
    return_on_equity = utils.fmt_pct(r["returnOnEquity"])
    profit_margin = utils.fmt_pct(r["profitMargins"])
    target_mean_price = utils.fmt(r["targetMeanPrice"])
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
        last_updated
        )

console.print(table)
