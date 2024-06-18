import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go

# Initialize volume_data as an empty DataFrame
volume_data = pd.DataFrame(columns=['timestamp', 'call_buy_volume', 'call_sell_volume', 'put_buy_volume', 'put_sell_volume'])

# Function to fetch options data
@st.cache
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

# Function to classify buy vs sell volume
def classify_volume(options_df):
    options_df['buy_volume'] = options_df.apply(
        lambda row: row['volume'] if row['lastPrice'] > (row['bid'] + row['ask']) / 2 else 0, axis=1)
    options_df['sell_volume'] = options_df.apply(
        lambda row: row['volume'] if row['lastPrice'] <= (row['bid'] + row['ask']) / 2 else 0, axis=1)
    return options_df

# Function to fetch and store options data with timestamp
@st.cache
def fetch_and_store_options_data(ticker, volume_threshold, oi_threshold):
    high_volume_calls, high_volume_puts = fetch_options_data(ticker, volume_threshold, oi_threshold)
    if high_volume_calls is None or high_volume_puts is None:
        return None, None

    # Add timestamp
    timestamp = datetime.now()
    high_volume_calls['timestamp'] = timestamp
    high_volume_puts['timestamp'] = timestamp

    # Classify volumes into buy and sell
    high_volume_calls = classify_volume(high_volume_calls)
    high_volume_puts = classify_volume(high_volume_puts)

    # Append new data to volume_data
    global volume_data
    volume_data = pd.concat([volume_data, high_volume_calls[['timestamp', 'buy_volume', 'sell_volume']],
                            high_volume_puts[['timestamp', 'buy_volume', 'sell_volume']]], ignore_index=True)

    return high_volume_calls, high_volume_puts

# Function to display options data
def display_options_data(ticker, volume_threshold, oi_threshold):
    high_volume_calls, high_volume_puts = fetch_and_store_options_data(ticker, volume_threshold, oi_threshold)

    if high_volume_calls is None or high_volume_puts is None:
        st.write("No options data found for the given ticker.")
        return

    # Display high-volume call options in a table
    st.write("High Volume Call Options")
    st.dataframe(high_volume_calls)

    # Display high-volume put options in a table
    st.write("High Volume Put Options")
    st.dataframe(high_volume_puts)

    # Aggregating volume data by timestamp
    call_volumes = high_volume_calls.groupby('timestamp')[['buy_volume', 'sell_volume']].sum().reset_index()
    put_volumes = high_volume_puts.groupby('timestamp')[['buy_volume', 'sell_volume']].sum().reset_index()

    # Merging data to ensure both call and put volumes are present for each timestamp
    call_volumes = call_volumes.rename(columns={'buy_volume': 'call_buy_volume', 'sell_volume': 'call_sell_volume'})
    put_volumes = put_volumes.rename(columns={'buy_volume': 'put_buy_volume', 'sell_volume': 'put_sell_volume'})
    volume_data_current = pd.merge(call_volumes, put_volumes, on='timestamp', how='outer').fillna(0)

    # Plotting the volume data as bar chart
    fig_volumes = go.Figure()

    fig_volumes.add_trace(go.Bar(
        x=volume_data_current['timestamp'],
        y=volume_data_current['call_buy_volume'],
        name='Call Buy Volume',
        marker_color='green'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data_current['timestamp'],
        y=volume_data_current['call_sell_volume'],
        name='Call Sell Volume',
        marker_color='darkgreen'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data_current['timestamp'],
        y=volume_data_current['put_buy_volume'],
        name='Put Buy Volume',
        marker_color='red'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data_current['timestamp'],
        y=volume_data_current['put_sell_volume'],
        name='Put Sell Volume',
        marker_color='darkred'
    ))

    fig_volumes.update_layout(
        barmode='group',
        title="Buy vs Sell Volumes by Timestamp",
        xaxis_title="Timestamp",
        yaxis_title="Volume",
        legend_title="Volume Type"
    )

    st.plotly_chart(fig_volumes)

    # Plotting the open interest data as bar chart similar to the provided image
    oi_calls = high_volume_calls.groupby('strike')['openInterest'].sum().reset_index()
    oi_puts = high_volume_puts.groupby('strike')['openInterest'].sum().reset_index()

    fig_oi = go.Figure()

    fig_oi.add_trace(go.Bar(
        x=oi_calls['strike'],
        y=oi_calls['openInterest'],
        name='Calls OI',
        marker_color='blue'
    ))

    fig_oi.add_trace(go.Bar(
        x=oi_puts['strike'],
        y=oi_puts['openInterest'],
        name='Puts OI',
        marker_color='red'
    ))

    fig_oi.update_layout(
        barmode='stack',
        title=f"Open Interest by Strike for {ticker}",
        xaxis_title="Strike Price",
        yaxis_title="Open Interest",
        legend_title="Option Type"
    )

    st.plotly_chart(fig_oi)

# Streamlit UI components
st.title("Options Data Display")

ticker = st.text_input('Enter stock ticker', 'GME')
volume_threshold = st.slider('Volume Threshold', 0, 10000, 5000, step=100)
oi_threshold = st.slider('Open Interest Threshold', 0, 10000, 1000, step=100)

if st.button('Fetch Options Data'):
    display_options_data(ticker, volume_threshold, oi_threshold)
