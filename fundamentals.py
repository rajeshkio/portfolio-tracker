import datetime
import utils
from rich.console import Console


def run():
    console = Console()
    # converting to string as type datetime is not JSON serializable
    dateNow = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")

    data = utils.load_json("portfolio.json")
    portfolio = data["portfolio"]
    fundamentals = []
    for stock in portfolio:
        try:
            fundamentals.append(utils.fetch_fundamentals(stock["ticker"], dateNow))
        except Exception as e:
            print(f"Skipping {stock['ticker']}: {e}")
    utils.save_json("fundamentals.json", fundamentals)

    # --- Display Tables ---
    fundamentals_table = utils.build_fundamentals_table(
        fundamentals, "Portfolio Tracker", dateNow
    )
    console.print(fundamentals_table)