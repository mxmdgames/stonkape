# stonkape
moarTA
# Stock Charting and Technical Analysis App

## Overview
This app is designed for advanced technical analysis of stock data. It allows users to visualize stock charts, apply various technical indicators, and analyze options data with a focus on high-volume options.

## Installation

1. **Clone the repository:**
    ```sh
    git clone <repository-url>
    cd <repository-directory>
    ```

2. **Install the required packages:**
    ```sh
    pip install streamlit yfinance pandas plotly ta
    ```

3. **Run the application:**
    ```sh
    streamlit run stock_charting_app2.py
    ```

## Features

- **Stock Data Visualization:** Displays candlestick charts with options to add technical indicators.
- **Technical Indicators:** Includes SMA, EMA, RSI, MACD, Bollinger Bands, Stochastic Oscillator, Ichimoku Cloud, and Parabolic SAR.
- **Volume Analysis:** Option to display volume and calculate key volume support levels.
- **Options Data:** Identifies high-volume call and put options.

## Usage

### User Interface

1. **Stock Ticker Input:**
    - Enter the stock ticker symbol (e.g., "AAPL").

2. **Time Frame Selection:**
    - Select the desired time frame from the dropdown menu.

3. **Refresh Data:**
    - Click the "Refresh Data" button to fetch the latest stock data.

4. **Technical Indicators:**
    - Select the desired indicators from the sidebar to overlay on the stock chart.

5. **Volume Display:**
    - Toggle the checkbox to show or hide volume bars on the chart.

6. **Trend Line Drawing:**
    - Enable or disable trend line drawing from the sidebar.

### Key Functionalities

- **Fetch Stock Data:**
    - Retrieves stock data from Yahoo Finance based on user input and selected time frame.

- **Technical Indicator Calculations:**
    - Implements various technical indicators using the `ta` library and integrates them into the chart.

- **Options Data Analysis:**
    - Fetches options data, filters high-volume options, and displays the top 10 most active calls and puts.

- **Support and Resistance Levels:**
    - Identifies and displays key support and resistance levels based on volume and price action.

## Custom Styling

The app applies custom CSS to ensure a professional look and feel. The background color, button styles, and input field styles are customized for better user experience.

## Example Code Snippet

```python
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
```

For a detailed implementation, refer to the full script provided in the repository.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with any enhancements, bug fixes, or new features.

## Contact

For any questions or feedback, please reach out to [warrenmadx@icloud.com].
