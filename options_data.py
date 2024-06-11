import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime

def fetch_options_data(ticker, volume_threshold, oi_threshold):
    stock = yf.Ticker(ticker)
    options_expiration_dates = stock.options

    if not options_expiration_dates:
        st.error("No options data found for the given ticker.")
        return None, None

    all_calls = []
    all_puts = []

    for options_date in options_expiration_dates:
        options_chain = stock.option_chain(options_date)

        calls = options_chain.calls
        puts = options_chain.puts

        # Calculate DTE
        dte = (pd.to_datetime(options_date) - datetime.now()).days

        calls['DTE'] = dte
        puts['DTE'] = dte

        high_volume_calls = calls[(calls['volume'] >= volume_threshold) & (calls['openInterest'] >= oi_threshold)].copy()
        high_volume_puts = puts[(puts['volume'] >= volume_threshold) & (puts['openInterest'] >= oi_threshold)].copy()

        all_calls.append(high_volume_calls)
        all_puts.append(high_volume_puts)

    all_calls_df = pd.concat(all_calls)
    all_puts_df = pd.concat(all_puts)

    return all_calls_df, all_puts_df

def display_options_data(ticker, volume_threshold, oi_threshold):
    try:
        high_volume_calls, high_volume_puts = fetch_options_data(ticker, volume_threshold, oi_threshold)

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
