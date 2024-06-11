import yfinance as yf
import pandas as pd
import streamlit as st

def fetch_options_data(ticker, volume_threshold):
    stock = yf.Ticker(ticker)
    options_expiration_dates = stock.options

    if not options_expiration_dates:
        st.error("No options data found for the given ticker.")
        return None, None

    options_date = options_expiration_dates[0]
    options_chain = stock.option_chain(options_date)

    calls = options_chain.calls
    puts = options_chain.puts

    high_volume_calls = calls[calls['volume'] >= volume_threshold].copy()
    high_volume_puts = puts[puts['volume'] >= volume_threshold].copy()

    return high_volume_calls, high_volume_puts

def display_options_data(ticker, volume_threshold):
    try:
        high_volume_calls, high_volume_puts = fetch_options_data(ticker, volume_threshold)

        if high_volume_calls is None or high_volume_puts is None:
            return

        st.subheader("High Volume Call Options")
        if not high_volume_calls.empty:
            st.write(high_volume_calls)
        else:
            st.write("No high volume call options found.")

        st.subheader("High Volume Put Options")
        if not high_volume_puts.empty:
            st.write(high_volume_puts)
        else:
            st.write("No high volume put options found.")
    except Exception as e:
        st.error(f"Error fetching options data: {e}")
