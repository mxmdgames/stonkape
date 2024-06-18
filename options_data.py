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

    # Display high-volume call options in a table
    st.write("High Volume Call Options")
    st.dataframe(high_volume_calls)

    # Display high-volume put options in a table
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
    

    fig_puts = go.Figure(data=[go.Table(
        header=dict(values=list(high_volume_puts.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[high_volume_puts[col] for col in high_volume_puts.columns],
                   fill_color='lavender',
                   align='left'))
    ])
    fig_puts.update_layout(title="High Volume Put Options")
    

    # Aggregating volume data by expiration date
    call_volumes = high_volume_calls.groupby('DTE')['volume'].sum().reset_index()
    put_volumes = high_volume_puts.groupby('DTE')['volume'].sum().reset_index()

    # Merging data to ensure both call and put volumes are present for each DTE
    volume_data = pd.merge(call_volumes, put_volumes, on='DTE', how='outer', suffixes=('_call', '_put')).fillna(0)

    # Plotting the volume data
    fig_volumes = go.Figure()

    fig_volumes.add_trace(go.Bar(
        x=volume_data['DTE'],
        y=volume_data['volume_call'],
        name='Call Volume',
        marker_color='green'
    ))

    fig_volumes.add_trace(go.Bar(
        x=volume_data['DTE'],
        y=volume_data['volume_put'],
        name='Put Volume',
        marker_color='red'
    ))

    fig_volumes.update_layout(
        barmode='group',
        title="Call vs Put Volumes by Expiration Date",
        xaxis_title="Days to Expiration (DTE)",
        yaxis_title="Volume",
        legend_title="Option Type"
    )

    st.plotly_chart(fig_volumes)

# Streamlit UI components
st.title("Options Data Display")

ticker = st.text_input('Enter stock ticker', 'GME')
volume_threshold = st.slider('Volume Threshold', 0, 10000, 5000, step=100)
oi_threshold = st.slider('Open Interest Threshold', 0, 10000, 1000, step=100)

if st.button('Fetch Options Data'):
    display_options_data(ticker, volume_threshold, oi_threshold)
