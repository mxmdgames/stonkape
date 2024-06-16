Here is the improved and refactored version of your Streamlit app code, with unnecessary code removed and without losing any functionality:

```python
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
from functools import lru_cache

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

    def calculate_stochastic_oscillator(data, window=14, smooth_window=3):
        stoch = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'], window=window, smooth_window=smooth_window)
        return stoch.stoch(), stoch.stoch_signal()

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
    data['%K'], data['%D'] = calculate_stochastic_oscillator(data)

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

    # Plotting the data
    fig = go.Figure()

    # Ensure the correct column name for datetime
    datetime_col = 'Datetime' if 'Datetime' in data.columns else 'Date'

    # Candlestick chart
    fig.add_trace(go.Candlestick(x=data[datetime_col], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlesticks'))

    # Add selected indicators
    if 'SMA' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['SMA'], mode='lines', name='SMA', line=dict(color='orange')))
    if 'EMA' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['EMA'], mode='lines', name='EMA', line=dict(color='purple')))
    if 'BBands' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['BB_High'], mode='lines', name='BB High', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['BB_Low'], mode='lines', name='BB Low', line=dict(color='red')))
    if 'Ichimoku Cloud' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_A'], mode='lines', name='Ichimoku A', line=dict(color='pink')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichim

oku_B'], mode='lines', name='Ichimoku B', line=dict(color='gray')))
    if 'Parabolic SAR' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR', marker=dict(color='green', symbol='circle')))

    # Add volume bars
    if show_volume:
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['Volume'], name='Volume', marker=dict(color='blue'), yaxis='y2'))

    # Update layout for dual y-axes
    fig.update_layout(yaxis2=dict(overlaying='y', side='right', title='Volume'), title=f"{ticker} Stock Price and Technical Indicators")

    # Plot RSI
    if 'RSI' in selected_indicators:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=data[datetime_col], y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
        fig_rsi.update_layout(title='Relative Strength Index (RSI)', yaxis=dict(title='RSI'))
        st.plotly_chart(fig_rsi, use_container_width=True)

    # Plot MACD
    if 'MACD' in selected_indicators:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
        fig_macd.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='red')))
        fig_macd.add_trace(go.Bar(x=data[datetime_col], y=data['MACD_Hist'], name='MACD Hist', marker=dict(color='green')))
        fig_macd.update_layout(title='MACD', yaxis=dict(title='MACD'))
        st.plotly_chart(fig_macd, use_container_width=True)

    # Plot OBV
    if 'OBV' in selected_indicators:
        fig_obv = go.Figure()
        fig_obv.add_trace(go.Scatter(x=data[datetime_col], y=data['OBV'], mode='lines', name='OBV', line=dict(color='blue')))
        fig_obv.update_layout(title='On-Balance Volume (OBV)', yaxis=dict(title='OBV'))
        st.plotly_chart(fig_obv, use_container_width=True)

    # Plot Stochastic Oscillator
    if '%K' in selected_indicators:
        fig_stoch = go.Figure()
        fig_stoch.add_trace(go.Scatter(x=data[datetime_col], y=data['%K'], mode='lines', name='%K', line=dict(color='blue')))
        fig_stoch.add_trace(go.Scatter(x=data[datetime_col], y=data['%D'], mode='lines', name='%D', line=dict(color='red')))
        fig_stoch.update_layout(title='Stochastic Oscillator', yaxis=dict(title='%K/%D'))
        st.plotly_chart(fig_stoch, use_container_width=True)

    # Display the main chart
    st.plotly_chart(fig, use_container_width=True)
```
