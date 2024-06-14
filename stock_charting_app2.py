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
    data = yf.download(ticker, period=period, interval=interval)
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
    selected_indicators = st.sidebar.multiselect("Select Indicators", ['SMA', 'EMA', 'RSI', 'MACD', 'Stochastic Oscillator', 'BBands', 'Ichimoku Cloud', 'Parabolic SAR', 'OBV'])

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
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_B'], mode='lines', name='Ichimoku B', line=dict(color='brown')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_Base'], mode='lines', name='Ichimoku Base Line', line=dict(color='yellow')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_Conv'], mode='lines', name='Ichimoku Conversion Line', line=dict(color='green')))
    if 'Parabolic SAR' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR', marker=dict(color='blue', symbol='circle')))
    if show_volume:
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['Volume'], name='Volume', marker=dict(color='blue'), yaxis='y2'))

    # Overlay Fibonacci retracement levels
    for level in fibonacci_levels:
        fig.add_hline(y=level, line=dict(color='purple', dash='dash'), name=f'Fib {level:.2f}')

    # Additional layout settings
    fig.update_layout(
        title=f'{ticker} Stock Price',
        yaxis_title='Price',
        xaxis_title='Date',
        template='plotly_dark',
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, position=0.15),
        height=800
    )

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)

    # Indicator plots
    if 'RSI' in selected_indicators:
        st.subheader("Relative Strength Index (RSI)")
        fig_rsi = go.Figure(go.Scatter(x=data[datetime_col], y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
        fig_rsi.update_layout(yaxis=dict(title='RSI'), height=300, template='plotly_dark')
        st.plotly_chart(fig_rsi, use_container_width=True)

    if 'MACD' in selected_indicators:
        st.subheader("MACD")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
        fig_macd.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD_Signal'], mode='lines', name='Signal', line=dict(color='red')))
        fig_macd.add_trace(go.Bar(x=data[datetime_col], y=data['MACD_Hist'], name='Hist', marker=dict(color='green')))
        fig_macd.update_layout(yaxis=dict(title='MACD'), height=300, template='plotly_dark')
        st.plotly_chart(fig_macd, use_container_width=True)

    if 'Stochastic Oscillator' in selected_indicators:
        st.subheader("Stochastic Oscillator")
        fig_stoch = go.Figure()
        fig_stoch.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch'], mode='lines', name='Stochastic', line=dict(color='blue')))
        fig_stoch.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch_Signal'], mode='lines', name='Signal', line=dict(color='red')))
        fig_stoch.update_layout(yaxis=dict(title='Stochastic'), height=300, template='plotly_dark')
        st.plotly_chart(fig_stoch, use_container_width=True)

    if 'OBV' in selected_indicators:
        st.subheader("On-Balance Volume (OBV)")
        fig_obv = go.Figure(go.Scatter(x=data[datetime_col], y=data['OBV'], mode='lines', name='OBV', line=dict(color='purple')))
        fig_obv.update_layout(yaxis=dict(title='OBV'), height=300, template='plotly_dark')
        st.plotly_chart(fig_obv, use_container_width=True)

    # Options data
    st.sidebar.title("Options Data")
    if st.sidebar.checkbox("Show Options Data"):
        expiry = st.sidebar.date_input("Select Expiry Date")
        options_chain = options_data.get_options_chain(ticker, expiry)
        if options_chain.empty:
            st.warning("No options data available for the selected expiry date.")
        else:
            st.subheader("Options Data")
            st.write(options_chain)

else:
    st.error("Unable to load data. Please check the ticker and time frame and try again.")
