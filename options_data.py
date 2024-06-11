import streamlit as st
import yfinance as yf
import pandas as pd


# Function to decode contract symbol
def decode_contract_symbol(contract_symbol):
    from datetime import datetime
    # Extract the ticker symbol, expiration date, option type, and strike price from the contract symbol
    ticker_symbol = contract_symbol[:-15]
    expiration_date = datetime.strptime(contract_symbol[-15:-9], '%y%m%d').date()
    option_type = 'Call' if contract_symbol[-9] == 'C' else 'Put'
    strike_price = int(contract_symbol[-8:]) / 1000

    return ticker_symbol, expiration_date, option_type, strike_price

@st.cache
def get_high_volume_options(ticker_symbol, 1000):
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
        high_volume_calls = calls_data[calls_data['volume'] > volume_threshold].copy()
        high_volume_puts = puts_data[puts_data['volume'] > volume_threshold].copy()

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

# Main function to display options data
def display_options_data(ticker, volume_threshold):
    # Fetch high volume options
    high_volume_options = options_data.get_high_volume_options(ticker, volume_threshold)

    # Create tables for top calls and puts
    top_calls = high_volume_options[high_volume_options['Type'] == 'Call'].nlargest(10, 'Volume')
    top_puts = high_volume_options[high_volume_options['Type'] == 'Put'].nlargest(10, 'Volume')

    # Display the tables
    st.subheader("Top 10 Most Active Calls")
    st.write(top_calls)

    st.subheader("Top 10 Most Active Puts")
    st.write(top_puts)

# Streamlit app setup
def main():
    st.title("High Volume Options Viewer")

    ticker = st.text_input("Enter a stock ticker symbol (e.g., AAPL):")
    volume_threshold = st.slider("Set volume threshold", min_value=100, max_value=10000, value=1000, step=100)

    if st.button("Options Data"):
        st.subheader("Options Data")
        if ticker:
            display_options_data(ticker, volume_threshold)
        else:
            st.warning("Please enter a ticker symbol.")

if __name__ == "__main__":
    main()
