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
    data = yf.download(ticker, period=period, interval=interval, progress=False) # Disable progress bar
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

    def calculate_stochastic_oscillator(data, window, smooth_window=3):
        stoch = ta.momentum.StochasticOscillator(
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            window=window,
            smooth_window=smooth_window
        )
        return stoch.stoch(), stoch.stoch_signal()

    def calculate_parabolic_sar(data):
        if data.empty or 'High' not in data.columns or 'Low' not in data.columns or 'Close' not in data.columns:
            st.error("Insufficient data to calculate Parabolic SAR.")
            return pd.Series([None] * len(data))
        return ta.trend.PSARIndicator(data['High'], data['Low'], data['Close']).psar()

    def calculate_obv(data):
        return ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()

    def calculate_ichimoku(data):
        ichimoku = ta.trend.IchimokuIndicator(data['High'], data['Low'])
        return ichimoku.ichimoku_a(), ichimoku.ichimoku_b(), ichimoku.ichimoku_base_line(), ichimoku.ichimoku_conversion_line()

    data['SMA'] = calculate_sma(data, window=20)
    data['EMA'] = calculate_ema(data, window=20)
    data['RSI'] = calculate_rsi(data, window=14)
    data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = calculate_macd(data)
    data['Stoch'], data['Stoch_Signal'] = calculate_stochastic_oscillator(data, window=14, smooth_window=3)
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
        fig        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR', marker=dict(color='cyan')))
    if 'OBV' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['OBV'], mode='lines', name='On Balance Volume', line=dict(color='blue')))
    if 'RSI' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['RSI'], mode='lines', name='RSI', line=dict(color='green')))
    if 'MACD' in selected_indicators:
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['MACD_Hist'], name='MACD Histogram', marker_color='grey'))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD'], mode='lines', name='MACD', line=dict(color='darkorange')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='firebrick')))
    if 'Stoch' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch'], mode='lines', name='Stochastic Oscillator', line=dict(color='magenta')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch_Signal'], mode='lines', name='Stochastic Signal', line=dict(color='blue')))

    # Add volume
    if show_volume:
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['Volume'], name='Volume', marker_color='grey'))

    # Adding trend lines
    if draw_trend_line:
        trendline = st.slider("Trend Line Length", 2, 100, 30)
        data['Trend_Up'] = ta.trend.ema_indicator(data['Close'], window=trendline)
        data['Trend_Down'] = ta.trend.sma_indicator(data['Close'], window=trendline)
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Trend_Up'], mode='lines', name='Trend Up', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Trend_Down'], mode='lines', name='Trend Down', line=dict(color='red')))

    # Update layout
    fig.update_layout(title=f"Technical Analysis for {ticker}", xaxis_title="Date", yaxis_title="Price", xaxis_rangeslider_visible=False)

    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    def calculate_fear_greed_index(data):
    # Normalize RSI to a 0-100 scale (0 = Fear, 100 = Greed)
    rsi_normalized = (data['RSI'] - data['RSI'].min()) / (data['RSI'].max() - data['RSI'].min()) * 100

    # Calculate the distance of the current close price from the SMA as a greed factor
    sma_distance = data['Close'] / data['SMA'] - 1
    sma_normalized = (sma_distance - sma_distance.min()) / (sma_distance.max() - sma_distance.min()) * 100

    # Normalize volume (higher volume can indicate higher greed)
    volume_normalized = (data['Volume'] - data['Volume'].min()) / (data['Volume'].max() - data['Volume'].min()) * 100

    # Combine the factors to create the index
    fear_greed_index = (rsi_normalized + sma_normalized + volume_normalized) / 3

    return fear_greed_index

# Assuming 'data' is your DataFrame containing 'RSI', 'Close', 'SMA', and 'Volume'
data['FearGreedIndex'] = calculate_fear_greed_index(data)

# Display Fear and Greed Index as a pressure gauge
st.subheader("Fear and Greed Index")

# Define ranges and colors for the gauge chart
ranges = [0, 20, 40, 60, 80, 100]
colors = ['#FF0000', '#FF4500', '#FFD700', '#32CD32', '#008000', '#006400']

# Create gauge chart
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=data['FearGreedIndex'].iloc[-1],  # Current Fear and Greed Index value
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Fear and Greed Index"},
    gauge={
        'axis': {'range': [None, 100], 'tickvals': ranges, 'ticktext': ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']},
        'bar': {'color': "black"},
        'steps': [
            {'range': [0, 20], 'color': '#FF0000'},
            {'range': [20, 40], 'color': '#FF4500'},
            {'range': [40, 60], 'color': '#FFD700'},
            {'range': [60, 80], 'color': '#32CD32'},
            {'range': [80, 100], 'color': '#008000'}
        ],
        'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': data['FearGreedIndex'].iloc[-1]}
    }
))

st.plotly_chart(fig)

# Display Fear and Greed Index as a line chart
st.subheader("Fear and Greed Index Over Time")
st.line_chart(data['FearGreedIndex'])

