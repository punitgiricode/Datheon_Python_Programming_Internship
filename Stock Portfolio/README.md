# Stock Portfolio Performance Tracker

A command-line utility that tracks an investment portfolio. You enter stock tickers, buy prices and share quantities; the program calculates total portfolio value, the gain/loss per holding (in money and %), and logs every run to a CSV file.

## Features

- Validates tickers against the S&P 500 dataset (`constituents.csv`)
- Stores positions in a dictionary; buying the same ticker twice merges into one position with a weighted-average buy price
- Fetches current prices live with `yfinance` (optional), with automatic fallback to manual price entry
- Calculates invested capital, current market value, gain/loss and gain/loss % per holding and for the whole portfolio
- Prints a formatted table to the console
- Appends results to `portfolio_summary.csv` using Python's built-in `csv` module (header is written once; each run is timestamped)

## Files

| File | Purpose |
|------|---------|
| `portfolio.py` | Main program |
| `constituents.csv` | S&P 500 ticker dataset (symbol, company, sector, etc.) |
| `portfolio_summary.csv` | Generated log of portfolio results (sample run included) |
| `README.md` | This file |

## Requirements

- Python 3.8+
- No packages needed for offline use
- Optional, for live prices: `pip install yfinance`

## Usage

```bash
# Live prices (needs yfinance and internet)
python portfolio.py

# Enter current prices manually
python portfolio.py --offline

# Use a different ticker dataset
python portfolio.py --csv path/to/constituents.csv
```

Keep `constituents.csv` in the same folder as `portfolio.py`.

### Example session

```
Ticker symbol: AAPL
  Apple Inc.
  Buy price per share: 150
  Number of shares: 10

Ticker symbol: MSFT
  Microsoft
  Buy price per share: 300
  Number of shares: 5

Ticker symbol:            <- press Enter to finish
```

### Example output

```
Symbol      Shares         Buy     Current      Invested         Value     Gain/Loss        %
---------------------------------------------------------------------------------------------
AAPL         15.00      156.67      190.00      2,350.00      2,850.00       +500.00  +21.28%
MSFT          5.00      300.00      420.00      1,500.00      2,100.00       +600.00  +40.00%
---------------------------------------------------------------------------------------------
TOTAL                                           4,650.00      5,850.00     +1,200.00  +25.81%
```

## How it works

1. `load_constituents()` reads the ticker dataset with `csv.DictReader`.
2. `collect_positions()` prompts for holdings and stores them as  
   `{"AAPL": {"shares": 15.0, "buy_price": 156.67}, ...}`.
3. `get_current_price()` tries `yfinance`; if unavailable or the lookup fails, it asks you for the price.
4. `evaluate_portfolio()` computes invested capital vs. market value for each holding and in total.
5. `print_report()` shows the table; `log_to_csv()` appends the results to `portfolio_summary.csv`.

## Output CSV columns

`Timestamp, Symbol, Company, Sector, Shares, Buy Price, Current Price, Invested, Market Value, Gain/Loss, Gain/Loss %, Price Source`

Each run adds one row per holding plus a `TOTAL` row.

## Notes

- `constituents.csv` contains ticker metadata only (no prices), so current prices come from `yfinance` or manual entry.
- Share class tickers such as `BRK.B` are converted to Yahoo's format (`BRK-B`) automatically for live lookups.
- Prices fetched live are the latest available close, which may be delayed.
- This tool is for learning and tracking purposes, not financial advice.
