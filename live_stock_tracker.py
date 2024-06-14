import yfinance as yf
import mplfinance as mpf
import pandas as pd
from datetime import datetime
import pytz
import time

def get_live_price(ticker):
    stock = yf.Ticker(ticker)
    try:
        data = stock.history(period="1d", interval="1m")  # Use 1-minute interval for better visualization
        return data
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def is_market_open():
    # Assuming the market is the New York Stock Exchange (NYSE)
    tz = pytz.timezone('America/New_York')
    now = datetime.now(tz)
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close and now.weekday() < 5

def track_live_prices(ticker):
    if not is_market_open():
        print("Market is closed. Live tracking will start when the market opens.")
        return

    while True:
        if not is_market_open():
            print("Market is closed. Live tracking will resume when the market opens.")
            time.sleep(60)  # Wait for a minute before checking again
            continue

        data = get_live_price(ticker)
        if data is not None and not data.empty:
            fig, ax = mpf.plot(data, type='candle', style='charles', title=f"{ticker} Live Candlestick Chart", returnfig=True)
            fig.show()
        else:
            print("No data available.")
        
        time.sleep(60)  # Update every minute

if __name__ == "__main__":
    track_live_prices("AAPL")  # You can change the ticker symbol here
