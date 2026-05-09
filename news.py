import datetime
import utils
from rich.console import Console

def run():
    dateNow = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    console = Console()
    # Load portfolio data from JSON file.
    data = utils.load_json("portfolio.json")

    # --- Fetch Portfolio ---
    portfolio = data["portfolio"]
    # --- Give News Prompt ---
    utils.show_news_prompt(portfolio, console)