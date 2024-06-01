## Installation for beginners ## **skip this section if you know what you are doing and you can read about the application below**

1. **Clone the repository:**
    - Open your web browser and go to the [Stonkape GitHub repository](https://github.com/mxmdgames/stonkape).
    - Click on the green "Code" button on the right side of the page.
    - You'll see a URL. Copy this URL. It should look something like `https://github.com/mxmdgames/stonkape.git`.
    - Open your command line interface (CLI), which could be Command Prompt on Windows, Terminal on macOS, or a Linux terminal.
    - Navigate to the directory where you want to clone the repository. You can do this by using the `cd` command followed by the path to the directory.
      For example:
      ```sh
      cd path/to/your/directory
      ```
    - Once you're in the right directory, paste the copied URL into the command line and press Enter.
      ```sh
      git clone https://github.com/mxmdgames/stonkape.git
      ```
    - Wait for the cloning process to complete. You should see a message indicating that the repository has been cloned successfully.
    - Now, navigate into the cloned repository directory:
      ```sh
      cd stonkape
      ```

2. **Install the required packages:**
    - To run the application, you need to install some Python packages. These can be installed using `pip`, which is a package manager for Python.
    - In your command line interface, enter the following command:
      ```sh
      pip install streamlit yfinance pandas plotly ta
      ```
    - This command will install the necessary packages for the application to work. Wait for the installation process to complete.

3. **Run the application:**
    - Now that you have cloned the repository and installed the required packages, you can run the application.
    - In your command line interface, enter the following command:
      ```sh
      streamlit run stock_charting_app2.py
      ```
    - This command starts the Streamlit application and launches it in your default web browser.
    - You should see the application interface loaded in your browser, and you can start using it to analyze stock data.

By following these steps, you'll be able to clone the repository, install the necessary packages, and run the Stock Charting and Technical Analysis App on your local machine. If you encounter any issues or have questions, feel free to reach out for further assistance!
Certainly! Here’s a detailed cheat sheet on various technical indicators for beginners, integrated into your existing structure:

# Stock Charting and Technical Analysis App

## Overview
This app is designed for advanced technical analysis of stock data. It allows users to visualize stock charts, apply various technical indicators, and analyze options data with a focus on high-volume options.

## Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/mxmdgames/stonkape.git
    cd stonkape
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

## Technical Indicators Cheat Sheet

### Simple Moving Average (SMA)
- **Bullish Signal**: Price crosses above SMA, indicating potential upward momentum.
- **Bearish Signal**: Price crosses below SMA, suggesting potential downward momentum.

### Exponential Moving Average (EMA)
- **Bullish Signal**: Price crosses above EMA, indicating potential bullish momentum.
- **Bearish Signal**: Price crosses below EMA, suggesting potential bearish momentum.

### Relative Strength Index (RSI)
- **Overbought Signal**: RSI above 70, suggesting potential overbought conditions and a possible reversal.
- **Oversold Signal**: RSI below 30, indicating potential oversold conditions and a possible buying opportunity.

### Moving Average Convergence Divergence (MACD)
- **Bullish Signal**: MACD line crosses above the signal line, indicating potential upward momentum.
- **Bearish Signal**: MACD line crosses below the signal line, suggesting potential downward momentum.

### Stochastic Oscillator
- **Overbought Signal**: Stochastic above 80, indicating potential overbought conditions and a possible reversal.
- **Oversold Signal**: Stochastic below 20, suggesting potential oversold conditions and a possible buying opportunity.

### Ichimoku Cloud (Kumo)
- **Bullish Signal**: Price above the cloud indicates potential bullish momentum and an uptrend.
- **Bearish Signal**: Price below the cloud indicates potential bearish momentum and a downtrend.
- **Cloud Twists**: Changes in the orientation of the cloud can signal shifts in market sentiment. Bullish twist when Senkou Span A crosses above Senkou Span B; bearish twist when it crosses below.

### Parabolic Stop and Reverse (Parabolic SAR)
- **Bullish Signal**: SAR below price, indicating potential upward momentum.
- **Bearish Signal**: SAR above price, suggesting potential downward momentum.

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

## GME IS FOR THE CHILDREN

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with any enhancements, bug fixes, or new features.

## Contact

For any questions or feedback, please reach out to [warrenmadx@icloud.com].
