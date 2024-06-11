import yfinance as yf
import streamlit as st

def display_options_data(ticker, volume_threshold):
    # Fetch options data
    try:
        stock = yf.Ticker(ticker)
        options_dates = stock.options

        if not options_dates:
            st.write("No options data available for this ticker.")
            return

        # Collect options data for all available expiration dates
        all_options_data = []
        for exp_date in options_dates:
            options_chain = stock.option_chain(exp_date)
            calls = options_chain.calls
            puts = options_chain.puts

            # Filter by volume threshold
            high_volume_calls = calls[calls['volume'] > volume_threshold]
            high_volume_puts = puts[puts['volume'] > volume_threshold]

            high_volume_calls['expirationDate'] = exp_date
            high_volume_puts['expirationDate'] = exp_date

            all_options_data.append(high_volume_calls)
            all_options_data.append(high_volume_puts)

        # Combine all high volume options into a single DataFrame
        high_volume_options = pd.concat(all_options_data)

        if high_volume_options.empty:
            st.write(f"No options with volume greater than {volume_threshold} found.")
        else:
            st.write(f"Options with volume greater than {volume_threshold}:")
            st.write(high_volume_options)

    except Exception as e:
        st.error(f"Error fetching options data: {e}")

# Ensure the script does not execute when imported as a module
if __name__ == "__main__":
    display_options_data('AAPL', 5000)
