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

# Function to classify buy vs sell volume
def classify_volume(options_df):
    options_df['buy_volume'] = options_df.apply(
        lambda row: row['volume'] if row['lastPrice'] > (row['bid'] + row['ask']) / 2 else 0, axis=1)
    options_df['sell_volume'] = options_df.apply(
        lambda row: row['volume'] if row['lastPrice'] <= (row['bid'] + row['ask']) / 2 else 0, axis=1)
    return options_df

# Function to display options data
def display_options_data(ticker, volume_threshold, oi_threshold):
    high_volume_calls, high_volume_puts = fetch_options_data(ticker, volume_threshold, oi_threshold)

    if high_volume_calls is None or high_volume_puts is None:
        st.write("No options data found for the given ticker.")
        return

    # Classify volumes into buy and sell
    high_volume_calls = classify_volume(high_volume_calls)
    high_volume_puts = classify_volume(high_volume_puts)

    # Display high-volume call options in a table
    st.write("High Volume Call Options")
    st.dataframe(high_volume_calls)

    # Display high-volume put options in a table
    st.write("High Volume Put Options")
    st.dataframe(high_volume_puts)

    # Aggregating volume data by expiration date
    call_volumes = high_volume_calls.groupby('DTE')[['buy_volume', 'sell_volume']].sum().reset_index()
    put_volumes = high_volume_puts.groupby('DTE')[['buy_volume', 'sell_volume']].sum().reset_index()

    # Merging data to ensure both call and put volumes are present for each DTE
    call_volumes = call_volumes.rename(columns={'buy_volume': 'call_buy_volume', 'sell_volume': 'call_sell_volume'})
    put_volumes = put_volumes.rename(columns={'buy_volume': 'put_buy_volume', 'sell_volume': 'put_sell_volume'})
    volume_data = pd.merge(call_volumes, put_volumes, on='DTE', how='outer').fillna(0)

    # Plotting the volume data as bar chart
    fig_volumes = go.Figure()

    fig_volumes.add_trace(go.Bar(
        x=volume_data['DTE'],
        y=volume_data['call_buy_volume'],
        name='Call Buy Volume',
        marker_color='green'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data['DTE'],
        y=volume_data['call_sell_volume'],
        name='Call Sell Volume',
        marker_color='darkgreen'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data['DTE'],
        y=volume_data['put_buy_volume'],
        name='Put Buy Volume',
        marker_color='red'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data['DTE'],
        y=volume_data['put_sell_volume'],
        name='Put Sell Volume',
        marker_color='darkred'
    ))

    fig_volumes.update_layout(
        barmode='group',
        title="Buy vs Sell Volumes by Expiration Date",
        xaxis_title="Days to Expiration (DTE)",
        yaxis_title="Volume",
        legend_title="Volume Type"
    )

    st.plotly_chart(fig_volumes)

    # Plotting the volume data as line chart
    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=volume_data['DTE'],
        y=volume_data['call_buy_volume'],
        mode='lines+markers',
        name='Call Buy Volume',
        line=dict(color='green')
    ))

    fig_line.add_trace(go.Scatter(
        x=volume_data['DTE'],
        y=volume_data['call_sell_volume'],
        mode='lines+markers',
        name='Call Sell Volume',
        line=dict(color='darkgreen')
    ))

    fig_line.add_trace(go.Scatter(
        x=volume_data['DTE'],
        y=volume_data['put_buy_volume'],
        mode='lines+markers',
        name='Put Buy Volume',
        line=dict(color='red')
    ))

    fig_line.add_trace(go.Scatter(
        x=volume_data['DTE'],
        y=volume_data['put_sell_volume'],
        mode='lines+markers',
        name='Put Sell Volume',
        line=dict(color='darkred')
    ))

    fig_line.update_layout(
        title="Buy vs Sell Volumes Over Time",
        xaxis_title="Days to Expiration (DTE)",
        yaxis_title="Volume",
        legend_title="Volume Type"
    )

    st.plotly_chart(fig_line)

# Streamlit UI components
st.title("Options Data Display")

ticker = st.text_input('Enter stock ticker', 'GME')
volume_threshold = st.slider('Volume Threshold', 0, 10000, 5000, step=100)
oi_threshold = st.slider('Open Interest Threshold', 0, 10000, 1000, step=100)

if st.button('Fetch Options Data'):
    display_options_data(ticker, volume_threshold, oi_threshold)
