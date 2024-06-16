import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go

# Function to fetch options data
def fetch_options_data(ticker, volume_threshold, oi_threshold):
    stock = yf.Ticker(ticker)
    options_expiration_dates = stock.options

    if not options_expiration_dates:
        return None, None

    all_calls = []
    all_puts = []

    for options_date in options_expiration_dates:
        options_chain = stock.option_chain(options_date)

        calls = options_chain.calls
        puts = options_chain.puts

        # Calculate DTE
        dte = (pd.to_datetime(options_date) - datetime.now()).days

        calls['DTE'] = f"{dte}DTE"
        puts['DTE'] = f"{dte}DTE"

        high_volume_calls = calls[(calls['volume'] >= volume_threshold) & (calls['openInterest'] >= oi_threshold)].copy()
        high_volume_puts = puts[(puts['volume'] >= volume_threshold) & (puts['openInterest'] >= oi_threshold)].copy()

        all_calls.append(high_volume_calls)
        all_puts.append(high_volume_puts)

    all_calls_df = pd.concat(all_calls)
    all_puts_df = pd.concat(all_puts)

    return all_calls_df, all_puts_df

# Function to display options data
def display_options_data(ticker, volume_threshold, oi_threshold):
    high_volume_calls, high_volume_puts = fetch_options_data(ticker, volume_threshold, oi_threshold)

    if high_volume_calls is None or high_volume_puts is None:
        st.write("No options data found for the given ticker.")
        return

    st.write("High Volume Call Options")
    st.dataframe(high_volume_calls)

    st.write("High Volume Put Options")
    st.dataframe(high_volume_puts)

    # Plotting the data in a table using Plotly for better visual representation
    fig_calls = go.Figure(data=[go.Table(
        header=dict(values=list(high_volume_calls.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[high_volume_calls[col] for col in high_volume_calls.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig_calls.update_layout(title="High Volume Call Options")
    st.plotly_chart(fig_calls)

    fig_puts = go.Figure(data=[go.Table(
        header=dict(values=list(high_volume_puts.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[high_volume_puts[col] for col in high_volume_puts.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig_puts.update_layout(title="High Volume Put Options")
   

# Streamlit UI components
st.title("Options Data Display")

ticker = st.text_input('Enter stock ticker', 'GME')
volume_threshold = st.slider('Volume Threshold', 0, 10000, 5000, step=100)
oi_threshold = st.slider('Open Interest Threshold', 0, 10000, 1000, step=100)

if st.button('Fetch Options Data'):
    display_options_data(ticker, volume_threshold, oi_threshold)
