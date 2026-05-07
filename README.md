# Stock Portfolio Tracker CLI

A terminal-based portfolio tracker for Indian and US stocks. 
Displays live prices, P&L, day change, and on-demand news headlines.

## Features
- Live prices via yfinance (NSE, BSE, US stocks)
- P&L in ₹ and % per holding
- Total portfolio P&L
- Watchlist tracking
- On-demand news headlines per ticker
- ETF support

## Preview

![Portfolio Tracker Screenshot](stock-portfolio.png)

## Setup

### 1. Clone the repository

```
git clone <your-repo-url>
cd stock-one
```

### 2. Create virtual environment
```
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```
pip3 install -r requirements.txt
```

### 4. Set up your portfolio
```
cp portfolio.json.example portfolio.json
```

Open portfolio.json and fill in your actual data:
- ticker: NSE stocks use TICKER.NS, BSE stocks use TICKER.BO, US stocks use ticker as-is
- buy_price: your average buy price
- qty: number of shares you hold

### 5. Run
```
python3 tracker.py
```

## Usage
- The table auto-renders with live prices on every run
- After the table, type any ticker symbol to fetch news headlines
- Press Enter with no input to exit
- Press Ctrl+C to exit anytime

## Portfolio JSON structure
```json
{
    "portfolio": [
        {"ticker": "HDFCBANK.NS", "buy_price": 929.78, "qty": 138}
    ],
    "watchlist": [
        {"ticker": "IRCTC.NS"}
    ]
}
```

## Supported exchanges
- NSE (India): append .NS to ticker
- BSE (India): append .BO to ticker  
- US stocks: use ticker directly (MSFT, AAPL etc)
