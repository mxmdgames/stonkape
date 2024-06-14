import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
from functools import lru_cache
from scipy.stats import norm
import numpy as np
import time
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
time_frame = st.selectbox("Select Time Frame", ["Intraday", "1 Day", "5 Day", "1 Month", "6 Months", "1 Year", "YTD", "5Y"])

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
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_Conv'], mode='lines', name='Ichimoku Conversion Line', line=dict(color='grey')))
    if 'Parabolic SAR' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR', marker=dict(color='green', symbol='circle', size=5)))

    # Add Fibonacci retracement levels
    for level in fibonacci_levels:
        fig.add_trace(go.Scatter(x=[data[datetime_col].iloc[0], data[datetime_col].iloc[-1]], y=[level, level], mode='lines', name=f'Fibonacci Level {level:.2f}', line=dict(dash='dash')))

    # Volume
    if show_volume:
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['Volume'], name='Volume', marker=dict(color='gray'), yaxis='y2'))

    # Layout settings
    fig.update_layout(
        title=f"Stock Data and Technical Indicators for {ticker}",
        yaxis_title='Stock Price',
        xaxis_title='Date',
        template='plotly_dark',
        yaxis2=dict(
            title='Volume',
            overlaying='y',
            side='right',
            showgrid=False,
        ),
        xaxis_rangeslider_visible=False,
        dragmode='drawline' if draw_trend_line else 'zoom'
    )

    # Plot additional technical indicators in separate subplots
    # RSI subplot
    rsi_fig = go.Figure()
    if 'RSI' in selected_indicators:
        rsi_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
        rsi_fig.update_layout(
            title="Relative Strength Index (RSI)",
            yaxis_title='RSI',
            xaxis_title='Date',
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
        )

    # MACD subplot
    macd_fig = go.Figure()
    if 'MACD' in selected_indicators:
        macd_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
        macd_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='red')))
        macd_fig.add_trace(go.Bar(x=data[datetime_col], y=data['MACD_Hist'], name='MACD Histogram'))
        macd_fig.update_layout(
            title="MACD (Moving Average Convergence Divergence)",
            yaxis_title='MACD',
            xaxis_title='Date',
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
        )

    # Stochastic Oscillator subplot
    stoch_fig = go.Figure()
    if 'Stochastic Oscillator' in selected_indicators:
        stoch_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch'], mode='lines', name='Stochastic Oscillator', line=dict(color='blue')))
        stoch_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch_Signal'], mode='lines', name='Stochastic Signal', line=dict(color='red')))
        stoch_fig.update_layout(
            title="Stochastic Oscillator",
            yaxis_title='Stochastic Oscillator',
            xaxis_title='Date',
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
        )

    # OBV subplot
    obv_fig = go.Figure()
    if 'OBV' in selected_indicators:
        obv_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['OBV'], mode='lines', name='OBV', line=dict(color='blue')))
        obv_fig.update_layout(
            title="On-Balance Volume (OBV)",
            yaxis_title='OBV',
            xaxis_title='Date',
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
        )

    # Render additional subplots
    if 'RSI' in selected_indicators:
        st.plotly_chart(rsi_fig, use_container_width=True)
    if 'MACD' in selected_indicators:
        st.plotly_chart(macd_fig, use_container_width=True)
    if 'Stochastic Oscillator' in selected_indicators:
        st.plotly_chart(stoch_fig, use_container_width=True)
    if 'OBV' in selected_indicators:
        st.plotly_chart(obv_fig, use_container_width=True)

    # Update Plotly chart config for scroll zoom behavior
    config = dict({'scrollZoom': not draw_trend_line})

    st.plotly_chart(fig, use_container_width=True, config=config)

    # Live Stock Price Tracker
    st.title("Live Stock Price Tracker")
    live_price_placeholder = st.empty()

    def get_live_price(ticker):
        ticker_data = yf.Ticker(ticker)
        todays_data = ticker_data.history(period='1d')
        return todays_data['Close'][0]

    while True:
        live_price = get_live_price(ticker)
        live_price_placeholder.metric(label=f"Live {ticker} Price", value=live_price)
        time.sleep(60)

    # Options Greeks Calculation
    def calculate_greeks(option_type, S, K, T, r, sigma):
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        if option_type == 'call':
            delta = norm.cdf(d1)
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * norm.cdf(d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)
        else:
            delta = -norm.cdf(-d1)
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * norm.cdf(-d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)
        return delta, gamma, theta, vega

    st.title("Options Greeks Analysis")

    option_type = st.selectbox("Select Option Type", ["call", "put"])
    strike_price = st.number_input("Enter Strike Price", min_value=0.0)
    expiration_date = st.date_input("Select Expiration Date")
    current_price = get_live_price(ticker)
    volatility = st.number_input("Enter Volatility", min_value=0.0)
    risk_free_rate = st.number_input("Enter Risk-Free Rate", min_value=0.0)

    days_to_expiration = (expiration_date - pd.Timestamp.today()).days / 365.0

    if st.button("Calculate Greeks"):
        delta, gamma, theta, vega = calculate_greeks(option_type, current_price, strike_price, days_to_expiration, risk_free_rate, volatility)
        st.write(f"Delta: {delta}")
        st.write(f"Gamma: {gamma}")
        st.write(f"Theta: {theta}")
        st.write(f"Vega: {vega}")

        # Plot Greeks
        greeks_fig = go.Figure()
        greeks_fig.add_trace(go.Scatter(x=[strike_price], y=[delta], mode='markers+lines', name='Delta'))
        greeks_fig.add_trace(go.Scatter(x=[strike_price], y=[gamma], mode='markers+lines', name='Gamma'))
        greeks_fig.add_trace(go.Scatter(x=[strike_price], y=[theta], mode='markers+lines', name='Theta'))
        greeks_fig.add_trace(go.Scatter(x=[strike_price], y=[vega], mode='markers+lines', name='Vega'))
        greeks_fig.update_layout(title="Options Greeks", xaxis_title="Strike Price", yaxis_title="Greek Value", template='plotly_dark')
        st.plotly_chart(greeks_fig, use_container_width=True)

else:
    st.error("Failed to load data. Please check the ticker symbol and date range.")

# Store the initial volume and OI thresholds in the session state
if 'volume_threshold' not in st.session_state:
    st.session_state.volume_threshold = 5000
if 'oi_threshold' not in st.session_state:
    st.session_state.oi_threshold = 1000

# Slider for volume threshold
VOLUME_THRESHOLD = st.slider("Volume Threshold", min_value=0, max_value=10000, value=st.session_state.volume_threshold, step=100)

# Slider for OI threshold
OI_THRESHOLD = st.slider("OI Threshold", min_value=0, max_value=10000, value=st.session_state.oi_threshold, step=100)

# Update session state with the new volume and OI thresholds
st.session_state.volume_threshold = VOLUME_THRESHOLD
st.session_state.oi_threshold = OI_THRESHOLD

# Fetch high volume options if button is pressed or if options data was previously shown
if st.button("Options Data") or 'options_data_shown' in st.session_state:
    st.subheader("Options Data")
    options_data.display_options_data(ticker, VOLUME_THRESHOLD, OI_THRESHOLD)
    st.session_state.options_data_shown = True
else:
    st.error("No data found for the given ticker and time frame.")
