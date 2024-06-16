import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
from functools import lru_cache
import options_data

# Set page config
st.set_page_config(page_title="Stock Charting and Technical Analysis App", layout="wide")

# Custom CSS for a professional look
st.markdown(
"""
<style>
body {
background-color: #1e1e1e;
color: #f0f0f0;
}
.stButton>button {
background-color: #4CAF50;
color: #f0f0f0;
}
.stTextInput>div>div>input {
background-color: #333333;
color: #f0f0f0;
}
</style>
""",
unsafe_allow_html=True
)

# Title and description
st.title("Stock Charting and Technical Analysis")
st.subheader("An advanced tool for technical analysis")

# User input for stock ticker and time frame
ticker = st.text_input("Enter Stock Ticker", value="GME", max_chars=10)

# Time frame selection
time_frame = st.selectbox("Select Time Frame", ["Intraday", "1 Day", "5 Day", "1 Month", "6 Months", "1 Year", "YTD", "5Y", "4 Hour"])

# Mapping time frames to yfinance intervals
time_frame_mapping = {
    "Intraday": "5m",
    "1 Day": "1d",
    "5 Day": "1d",
    "1 Month": "1d",
    "6 Months": "1d",
    "1 Year": "1d",
    "YTD": "1d",
    "5Y": "1d",
}

period_mapping = {
    "Intraday": "1d",
    "1 Day": "1d",
    "5 Day": "5d",
    "1 Month": "1mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "YTD": "ytd",
    "5Y": "5y",
}

# Initialize period and interval
interval = time_frame_mapping[time_frame]
period = period_mapping[time_frame]

# Function to aggregate data
def aggregate_data(data, interval):
    if interval == "1h":
        return data.resample('H').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna().reset_index()
    elif interval == "4h":
        return data.resample('4H').agg({
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }).dropna().reset_index()
    else:
        return data

# Function to load data without caching
@lru_cache(maxsize=None)
def load_data_uncached(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval, progress=False)  # Disable progress bar
    if data.empty:
        st.error("No data found for the given ticker and time frame.")
        return data
    if data.index.tzinfo is not None:
        data.index = data.index.tz_localize(None)
    if interval in ["1h", "4h"]:
        data = aggregate_data(data, interval)
        data.reset_index(inplace=True)
    return data

# Fetching stock data
def load_data(ticker, period, interval):
    return load_data_uncached(ticker, period, interval)

def refresh_data(ticker, period, interval):
    data = load_data_uncached(ticker, period, interval)
    return data

# Refresh button
if st.button("Refresh Data"):
    data = refresh_data(ticker, period, interval)
else:
    data = load_data(ticker, period, interval)

# Check if data is loaded before proceeding
if not data.empty:
    # Display raw data
    st.subheader("Raw Data")
    st.write(data.tail())

    # Calculate technical indicators
    def calculate_sma(data, window):
        return ta.trend.SMAIndicator(data['Close'], window=window).sma_indicator()

    def calculate_ema(data, window):
        return ta.trend.EMAIndicator(data['Close'], window=window).ema_indicator()

    def calculate_rsi(data, window):
        return ta.momentum.RSIIndicator(data['Close'], window=window).rsi()

    def calculate_macd(data):
        macd = ta.trend.MACD(data['Close'])
        return macd.macd(), macd.macd_signal(), macd.macd_diff()

    def calculate_bbands(data):
        bbands = ta.volatility.BollingerBands(data['Close'])
        return bbands.bollinger_hband(), bbands.bollinger_lband()

    def calculate_stochastic_oscillator(data):
        so = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
        return so.stoch(), so.stoch_signal()

    def calculate_obv(data):
        return ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()

    def calculate_ichimoku(data):
        ichimoku = ta.trend.IchimokuIndicator(data['High'], data['Low'])
        return ichimoku.ichimoku_a(), ichimoku.ichimoku_b(), ichimoku.ichimoku_base_line(), ichimoku.ichimoku_conversion_line()

    def calculate_parabolic_sar(data):
        if data.empty or 'High' not in data.columns or 'Low' not in data.columns or 'Close' not in data.columns:
            st.error("Insufficient data to calculate Parabolic SAR.")
            return pd.Series([None] * len(data))
        return ta.trend.PSARIndicator(data['High'], data['Low'], data['Close']).psar()

    data['SMA'] = calculate_sma(data, window=20)
    data['EMA'] = calculate_ema(data, window=20)
    data['RSI'] = calculate_rsi(data, window=14)
    data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = calculate_macd(data)
    data['Stoch'], data['Stoch_Signal'] = calculate_stochastic_oscillator(data)
    data['BB_High'], data['BB_Low'] = calculate_bbands(data)
    data['Ichimoku_A'], data['Ichimoku_B'], data['Ichimoku_Base'], data['Ichimoku_Conv'] = calculate_ichimoku(data)
    data['Parabolic_SAR'] = calculate_parabolic_sar(data)
    data['OBV'] = calculate_obv(data)

    # Add checkboxes for indicators
    st.sidebar.title("Technical Indicators")
    selected_indicators = st.sidebar.multiselect("Select Indicators", ['SMA', 'EMA', 'RSI', 'MACD', 'BBands', 'Ichimoku Cloud', 'Parabolic SAR', 'OBV'])

    # Add volume checkbox
    show_volume = st.sidebar.checkbox("Show Volume")

    # Add trend line drawing toggle
    draw_trend_line = st.sidebar.checkbox("Enable Trend Line Drawing")

    # Calculate Fibonacci retracement levels
    def calculate_fibonacci_retracement(data):
        max_price = data['High'].max()
        min_price = data['Low'].min()
        diff = max_price - min_price
        levels = [max_price - 0.236 * diff, max_price - 0.382 * diff, max_price - 0.5 * diff, max_price - 0.618 * diff, min_price]
        return levels

    fibonacci_levels = calculate_fibonacci_retracement(data)

    # Calculate Fear and Greed Index
    def calculate_fear_greed_index(data):
        fear_greed_index = pd.Series(index=data.index, dtype=float)

        # Normalize RSI to a 0-1 scale (0 = Fear, 1 = Greed)
        rsi_normalized = data['RSI'] / 100

        # Use the distance of the current close price from the SMA as a greed factor
        sma_distance = data['Close'] / data['SMA'] - 1
        sma_normalized = (sma_distance - sma_distance.min()) / (sma_distance.max() - sma_distance.min())

        # Use volume as a proxy for market sentiment (higher volume can indicate higher greed)
        volume_normalized = (data['Volume'] - data['Volume'].min()) / (data['Volume'].max() - data['Volume'].min())

        # Combine the factors to create the index
        fear_greed_index = (rsi_normalized + sma_normalized + volume_normalized) / 3

        return fear_greed_index

    data['FearGreedIndex'] = calculate_fear_greed_index(data)

    # Display Fear and Greed Index
    st.subheader("Fear and Greed Index")
    st.line_chart(data['FearGreedIndex'])

    # Plotting the data
    fig = go.Figure()

    # Determine the correct datetime column
    datetime_column = 'Datetime' if 'Datetime' in data.columns else 'Date'

    # Add main plot
    fig.add_trace(go.Candlestick(
        x=data.index if datetime_column == 'Datetime' else data[datetime_column],
        open=data['Open'],
        high=data['High'],
        low=data['Low'],
        close=data['Close'],
        name='Candlestick'
    ))

    # Add volume bars
    if show_volume:
        fig.add_trace(go.Bar(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['Volume'], name='Volume', yaxis='y2', marker=dict(color='lightgray', opacity=0.5)))

    # Add selected indicators to the plot
    if 'SMA' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['SMA'], mode='lines', name='SMA'))
    if 'EMA' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['EMA'], mode='lines', name='EMA'))
    if 'RSI' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['RSI'], mode='lines', name='RSI', yaxis='y3'))
    if 'MACD' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['MACD'], mode='lines', name='MACD'))
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['MACD_Signal'], mode='lines', name='MACD Signal'))
        fig.add_trace(go.Bar(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['MACD_Hist'], name='MACD Hist', yaxis='y4'))
    if 'BBands' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['BB_High'], mode='lines', name='BB High'))
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['BB_Low'], mode='lines', name='BB Low'))
    if 'Ichimoku Cloud' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['Ichimoku_A'], mode='lines', name='Ichimoku A'))
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['Ichimoku_B'], mode='lines', name='Ichimoku B'))
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['Ichimoku_Base'], mode='lines', name='Ichimoku Base'))
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['Ichimoku_Conv'], mode='lines', name='Ichimoku Conv'))
    if 'Parabolic SAR' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR', marker=dict(size=2)))
    if 'OBV' in selected_indicators:
        fig.add_trace(go.Scatter(x=data.index if datetime_column == 'Datetime' else data[datetime_column], y=data['OBV'], mode='lines', name='OBV', yaxis='y5'))

    # Add Fibonacci retracement levels
    for level in fibonacci_levels:
        fig.add_trace(go.Scatter(x=[data.index[0], data.index[-1]], y=[level, level], mode='lines', line=dict(dash='dash', color='purple'), name=f'Fib Level {level:.2f}'))

    # Trend line drawing
    if draw_trend_line:
        st.info("Click on the chart to start and end the trend line.")
        trend_line = st.plotly_chart(fig, use_container_width=True, config=dict(editable=True))
    else:
        st.plotly_chart(fig, use_container_width=True)

    # Calculate option Greeks and IV
    st.subheader("Options Greeks and Implied Volatility")
    expiry_dates = options_data.get_expiry_dates(ticker)
    selected_expiry = st.selectbox("Select Expiry Date", expiry_dates)

    # Fetch and display options data
    options_df = options_data.get_options_data(ticker, selected_expiry)
    st.write(options_df)
else:
    st.error("No data available for the selected ticker and time frame.")
