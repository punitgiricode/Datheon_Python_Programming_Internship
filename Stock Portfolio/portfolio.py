"""Stock Portfolio Performance Tracker.

Enter stock tickers, buy prices and share quantities. The program validates
tickers against the S&P 500 dataset (constituents.csv), looks up current
prices, reports total portfolio value and the percentage gain/loss per
holding, and logs the summary to portfolio_summary.csv.

Usage:
    python portfolio.py                 # live prices via yfinance (if installed)
    python portfolio.py --offline       # skip live lookup, type prices manually
    python portfolio.py --csv path.csv  # use a different ticker dataset
"""

import argparse
import csv
import os
from datetime import datetime

CONSTITUENTS_FILE = "constituents.csv"
SUMMARY_FILE = "portfolio_summary.csv"

SUMMARY_FIELDS = [
    "Timestamp", "Symbol", "Company", "Sector", "Shares", "Buy Price",
    "Current Price", "Invested", "Market Value", "Gain/Loss", "Gain/Loss %",
    "Price Source",
]


# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
def load_constituents(path):
    """Return {symbol: {"name": ..., "sector": ...}} from the S&P 500 CSV."""
    companies = {}
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                companies[row["Symbol"].strip().upper()] = {
                    "name": row["Security"].strip(),
                    "sector": row["GICS Sector"].strip(),
                }
    except FileNotFoundError:
        print(f"Warning: '{path}' not found. Tickers will not be validated.")
    return companies


# --------------------------------------------------------------------------
# Price lookup
# --------------------------------------------------------------------------
def fetch_live_price(symbol):
    """Try to get the latest price from yfinance. Returns float or None."""
    try:
        import yfinance as yf
    except ImportError:
        return None
    try:
        # Yahoo uses '-' where the S&P list uses '.' (e.g. BRK.B -> BRK-B)
        ticker = yf.Ticker(symbol.replace(".", "-"))
        history = ticker.history(period="5d")
        if not history.empty:
            return float(history["Close"].iloc[-1])
    except Exception:
        pass
    return None


def get_current_price(symbol, offline=False):
    """Return (price, source). Falls back to manual entry if live fails."""
    if not offline:
        price = fetch_live_price(symbol)
        if price is not None:
            return price, "live (yfinance)"
        print(f"  Could not fetch a live price for {symbol}.")
    price = read_number(f"  Enter current price for {symbol}: ", minimum=0.0)
    return price, "manual"


# --------------------------------------------------------------------------
# Input helpers
# --------------------------------------------------------------------------
def read_number(prompt, minimum=0.0, allow_equal=False):
    """Keep asking until the user enters a valid number above `minimum`."""
    while True:
        raw = input(prompt).strip().replace(",", "")
        try:
            value = float(raw)
        except ValueError:
            print("  Please enter a number.")
            continue
        if value > minimum or (allow_equal and value == minimum):
            return value
        print(f"  Value must be greater than {minimum}.")


def collect_positions(companies):
    """Interactively build the portfolio dictionary.

    portfolio = {"AAPL": {"shares": 10.0, "buy_price": 150.0}, ...}
    Buying the same ticker twice merges into one position using a
    weighted-average buy price.
    """
    portfolio = {}
    print("Enter your holdings. Press Enter on the ticker prompt when done.\n")
    while True:
        symbol = input("Ticker symbol: ").strip().upper()
        if not symbol:
            if portfolio:
                break
            print("  Add at least one holding first.")
            continue
        if companies and symbol not in companies:
            print(f"  '{symbol}' is not in the S&P 500 dataset. Try again.")
            continue

        label = companies.get(symbol, {}).get("name", symbol)
        print(f"  {label}")
        buy_price = read_number("  Buy price per share: ")
        shares = read_number("  Number of shares: ")

        if symbol in portfolio:
            old = portfolio[symbol]
            total_shares = old["shares"] + shares
            avg = (old["shares"] * old["buy_price"] + shares * buy_price) / total_shares
            portfolio[symbol] = {"shares": total_shares, "buy_price": avg}
            print("  Added to existing position (average buy price updated).")
        else:
            portfolio[symbol] = {"shares": shares, "buy_price": buy_price}
        print()
    return portfolio


# --------------------------------------------------------------------------
# Calculations
# --------------------------------------------------------------------------
def evaluate_portfolio(portfolio, companies, offline=False):
    """Return (rows, totals) with per-holding and overall performance."""
    print("\nLooking up current prices...")
    rows = []
    for symbol, pos in portfolio.items():
        price, source = get_current_price(symbol, offline)
        invested = pos["shares"] * pos["buy_price"]
        value = pos["shares"] * price
        gain = value - invested
        rows.append({
            "Symbol": symbol,
            "Company": companies.get(symbol, {}).get("name", symbol),
            "Sector": companies.get(symbol, {}).get("sector", ""),
            "Shares": pos["shares"],
            "Buy Price": pos["buy_price"],
            "Current Price": price,
            "Invested": invested,
            "Market Value": value,
            "Gain/Loss": gain,
            "Gain/Loss %": gain / invested * 100,
            "Price Source": source,
        })

    total_invested = sum(r["Invested"] for r in rows)
    total_value = sum(r["Market Value"] for r in rows)
    total_gain = total_value - total_invested
    totals = {
        "Invested": total_invested,
        "Market Value": total_value,
        "Gain/Loss": total_gain,
        "Gain/Loss %": total_gain / total_invested * 100,
    }
    return rows, totals


# --------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------
def print_report(rows, totals):
    header = (f"{'Symbol':<8}{'Shares':>10}{'Buy':>12}{'Current':>12}"
              f"{'Invested':>14}{'Value':>14}{'Gain/Loss':>14}{'%':>9}")
    line = "=" * len(header)
    print(f"\n{line}\nPORTFOLIO SUMMARY  ({datetime.now():%Y-%m-%d %H:%M})\n{line}")
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['Symbol']:<8}{r['Shares']:>10,.2f}{r['Buy Price']:>12,.2f}"
              f"{r['Current Price']:>12,.2f}{r['Invested']:>14,.2f}"
              f"{r['Market Value']:>14,.2f}{r['Gain/Loss']:>+14,.2f}"
              f"{r['Gain/Loss %']:>+8.2f}%")
    print("-" * len(header))
    print(f"{'TOTAL':<8}{'':>10}{'':>12}{'':>12}{totals['Invested']:>14,.2f}"
          f"{totals['Market Value']:>14,.2f}{totals['Gain/Loss']:>+14,.2f}"
          f"{totals['Gain/Loss %']:>+8.2f}%")
    print(line)


def log_to_csv(rows, totals, path=SUMMARY_FILE):
    """Append this run to the summary CSV (header written only once)."""
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_file = not os.path.exists(path) or os.path.getsize(path) == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        if new_file:
            writer.writeheader()
        for r in rows:
            writer.writerow({
                "Timestamp": stamp,
                **{k: (f"{v:.2f}" if isinstance(v, float) else v)
                   for k, v in r.items()},
            })
        writer.writerow({
            "Timestamp": stamp, "Symbol": "TOTAL",
            **{k: f"{v:.2f}" for k, v in totals.items()},
        })
    print(f"\nSummary logged to '{path}'.")


# --------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Stock Portfolio Performance Tracker")
    parser.add_argument("--csv", default=CONSTITUENTS_FILE,
                        help="S&P 500 ticker dataset (default: constituents.csv)")
    parser.add_argument("--offline", action="store_true",
                        help="skip live price lookup and enter prices manually")
    args = parser.parse_args()

    companies = load_constituents(args.csv)
    portfolio = collect_positions(companies)
    rows, totals = evaluate_portfolio(portfolio, companies, args.offline)
    print_report(rows, totals)
    log_to_csv(rows, totals)


if __name__ == "__main__":
    main()
