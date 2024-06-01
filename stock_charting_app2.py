import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
from functools import lru_cache

# Terminal start: streamlit run stock_charting_app2.py

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
ticker = st.text_input("Enter Stock Ticker", value="AAPL", max_chars=10)

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
    "4 Hour": "4h"
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
    "4 Hour": "1mo"
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
    data['MACD'], data['MACD_Signal'], data['MACD_Diff'] = calculate_macd(data)
    data['BB_High'], data['BB_Low'] = calculate_bbands(data)
    data['Stoch'], data['Stoch_Signal'] = calculate_stochastic_oscillator(data)
    data['Ichimoku_A'], data['Ichimoku_B'], data['Ichimoku_Base'], data['Ichimoku_Conv'] = calculate_ichimoku(data)
    data['Parabolic_SAR'] = calculate_parabolic_sar(data)

    # Add checkboxes for indicators
    st.sidebar.title("Technical Indicators")
    selected_indicators = st.sidebar.multiselect("Select Indicators", ['SMA', 'EMA', 'RSI', 'MACD', 'BBands', 'Stochastic Oscillator', 'Ichimoku Cloud', 'Parabolic SAR'])

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
    if 'RSI' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
    if 'MACD' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD'], mode='lines', name='MACD', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='red')))
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['MACD_Diff'], name='MACD Diff', marker=dict(color='gray')))
    if 'BBands' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['BB_High'], mode='lines', name='BB High', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['BB_Low'], mode='lines', name='BB Low', line=dict(color='red')))
    if 'Stochastic Oscillator' in selected_indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch'], mode='lines', name='Stochastic Oscillator', line=dict(color='cyan')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch_Signal'], mode='lines', name='Stochastic Oscillator Signal', line=dict(color='magenta')))
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
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)

    # Define a threshold for high volume
    VOLUME_THRESHOLD = 1000

    # Function to decode contract symbol
    def decode_contract_symbol(contract_symbol):
        from datetime import datetime
        # Extract the ticker symbol, expiration date, option type, and strike price from the contract symbol
        ticker_symbol = contract_symbol[:-15]
        expiration_date = datetime.strptime(contract_symbol[-15:-9], '%y%m%d').date()
        option_type = 'Call' if contract_symbol[-9] == 'C' else 'Put'
        strike_price = int(contract_symbol[-8:]) / 1000

        return ticker_symbol, expiration_date, option_type, strike_price

    @st.cache_data
    def get_high_volume_options(ticker_symbol):
        # Create a ticker object
        ticker = yf.Ticker(ticker_symbol)

        # Get all expiry dates
        expiry_dates = ticker.options

        # Initialize an empty DataFrame to store all high volume options
        high_volume_options = pd.DataFrame()

        # Loop through all expiry dates
        for expiry_date in expiry_dates:
            # Get options data for this expiry date
            options_data = ticker.option_chain(expiry_date)

            # The returned data is a named tuple containing two dataframes: calls and puts
            calls_data = options_data.calls
            puts_data = options_data.puts

            # Filter for high volume options
            high_volume_calls = calls_data[calls_data['volume'] > VOLUME_THRESHOLD].copy()
            high_volume_puts = puts_data[puts_data['volume'] > VOLUME_THRESHOLD].copy()

            # Add option type column
            if not high_volume_calls.empty:
                high_volume_calls.loc[:, 'Option Type'] = 'Call'
            if not high_volume_puts.empty:
                high_volume_puts.loc[:, 'Option Type'] = 'Put'

            # Concatenate calls and puts data
            high_volume_options_date = pd.concat([high_volume_calls, high_volume_puts])

            # Append to the overall DataFrame
            high_volume_options = pd.concat([high_volume_options, high_volume_options_date])

        # Decode contract symbols
        high_volume_options[['Ticker Symbol', 'Expiration Date', 'Option Type', 'Strike Price']] = high_volume_options.apply(lambda row: decode_contract_symbol(row['contractSymbol']), axis=1, result_type='expand')

        # Reorder and rename columns to match the screenshot
        high_volume_options = high_volume_options[['Ticker Symbol', 'contractSymbol', 'Expiration Date', 'lastTradeDate', 'Strike Price', 'lastPrice', 'bid', 'ask', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility', 'inTheMoney', 'Option Type']]
        high_volume_options.columns = ['Ticker', 'Contract', 'DTE', 'Last Trade Date', 'Strike', 'Last', 'Bid', 'Ask', 'Change', 'Percent Change', 'Volume', 'Open Interest', 'IV', 'ITM', 'Type']

        return high_volume_options

    # Fetch high volume options
    high_volume_options = get_high_volume_options(ticker)

    # Create tables for top calls and puts
    top_calls = high_volume_options[high_volume_options['Type'] == 'Call'].nlargest(10, 'Volume')
    top_puts = high_volume_options[high_volume_options['Type'] == 'Put'].nlargest(10, 'Volume')

    # Display the tables
    st.subheader("Top 10 Most Active Calls")
    st.write(top_calls)

    st.subheader("Top 10 Most Active Puts")
    st.write(top_puts)



    # Calculate key volume support
    def calculate_key_volume_support(data):
        volume_price = data[['Close', 'Volume']].copy()
        volume_price['Volume x Close'] = volume_price['Close'] * volume_price['Volume']

        # Group by price levels and calculate the volume x close
        volume_support_levels = volume_price.groupby('Close')['Volume x Close'].sum()

        # Find the price level with the highest volume x close (strongest support)
        highest_volume_support_level = volume_support_levels.idxmax()

        # Find the price level with the lowest volume x close (weakest support)
        lowest_volume_support_level = volume_support_levels.idxmin()

        return highest_volume_support_level, lowest_volume_support_level

    # Identify support and resistance levels
    def identify_support_resistance(data):
        pivots = []
        max_list = []
        min_list = []
        for i in range(1, len(data)-1):
            if data['Low'][i] < data['Low'][i-1] and data['Low'][i] < data['Low'][i+1]:
                pivots.append((data[datetime_col][i], data['Low'][i]))
                min_list.append((data[datetime_col][i], data['Low'][i]))
            if data['High'][i] > data['High'][i-1] and data['High'][i] > data['High'][i+1]:
                pivots.append((data[datetime_col][i], data['High'][i]))
                max_list.append((data[datetime_col][i], data['High'][i]))

        return pivots, max_list, min_list

    # Calculate and display key volume support
    highest_volume_support, lowest_volume_support = calculate_key_volume_support(data)
    st.write(f"Key Volume Support Level: Highest - {highest_volume_support}, Lowest - {lowest_volume_support}")

    # Calculate and display support and resistance levels
    pivots, max_list, min_list = identify_support_resistance(data)
    st.write("Support and Resistance Levels:")
    st.write("Pivots:", pivots)
    st.write("Max Levels:", max_list)
    st.write("Min Levels:", min_list)

else:
    st.error("Failed to load data. Please check the ticker symbol and date range.")
