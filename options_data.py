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
def get_high_volume_options(ticker_symbol, volume_threshold=1000):
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
