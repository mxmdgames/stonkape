import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ta
import options_data  # Ensure you have this module implemented

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dbc.Row(dbc.Col(html.H1("Stock Charting and Technical Analysis App"), width={'size': 6, 'offset': 3})),
    dbc.Row(dbc.Col(dcc.Input(id='ticker-input', type='text', value='GME', maxLength=10, style={'width': '50%'}), width={'size': 6, 'offset': 3})),
    dbc.Row(dbc.Col(dcc.Dropdown(
        id='time-frame-dropdown',
        options=[
            {'label': 'Intraday', 'value': 'Intraday'},
            {'label': '1 Day', 'value': '1 Day'},
            {'label': '5 Day', 'value': '5 Day'},
            {'label': '1 Month', 'value': '1 Month'},
            {'label': '6 Months', 'value': '6 Months'},
            {'label': '1 Year', 'value': '1 Year'},
            {'label': 'YTD', 'value': 'YTD'},
            {'label': '5Y', 'value': '5Y'},
            {'label': '4 Hour', 'value': '4 Hour'},
        ],
        value='1 Year',
        style={'width': '50%'}
    ), width={'size': 6, 'offset': 3})),
    dbc.Row(dbc.Col(dbc.Button('Refresh Data', id='refresh-button', n_clicks=0), width={'size': 6, 'offset': 3})),
    dbc.Row(dbc.Col(dcc.Graph(id='stock-chart'), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(dcc.Checklist(
        id='indicators-checklist',
        options=[
            {'label': 'SMA', 'value': 'SMA'},
            {'label': 'EMA', 'value': 'EMA'},
            {'label': 'RSI', 'value': 'RSI'},
            {'label': 'MACD', 'value': 'MACD'},
            {'label': 'Stochastic Oscillator', 'value': 'Stochastic Oscillator'},
            {'label': 'BBands', 'value': 'BBands'},
            {'label': 'Ichimoku Cloud', 'value': 'Ichimoku Cloud'},
            {'label': 'Parabolic SAR', 'value': 'Parabolic SAR'},
            {'label': 'OBV', 'value': 'OBV'},
        ],
        value=['SMA', 'EMA', 'RSI'],
        inline=True
    ), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(dcc.Graph(id='additional-charts'), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(html.Div(id='fibonacci-levels', style={'width': '100%'}), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(dcc.Slider(id='volume-threshold', min=0, max=10000, step=100, value=5000, marks={i: str(i) for i in range(0, 10001, 2000)}), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(dcc.Slider(id='oi-threshold', min=0, max=10000, step=100, value=1000, marks={i: str(i) for i in range(0, 10001, 2000)}), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(dcc.Graph(id='options-chart'), width={'size': 10, 'offset': 1})),
    dbc.Row(dbc.Col(dcc.Graph(id='fear-greed-index'), width={'size': 10, 'offset': 1})),
])

time_frame_mapping = {
    "Intraday": "5m",
    "1 Day": "1d",
    "5 Day": "1d",
    "1 Month": "1d",
    "6 Months": "1d",
    "1 Year": "1d",
    "YTD": "1d",
    "5Y": "1d",
    "4 Hour": "1h",
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

def load_data(ticker, period, interval):
    data = yf.download(ticker, period=period, interval=interval)
    if data.empty:
        return data
    if interval in ["1h", "4h"]:
        data = aggregate_data(data, interval)
    data.reset_index(inplace=True)
    return data

def calculate_technical_indicators(data):
    data['SMA'] = ta.trend.SMAIndicator(data['Close'], window=20).sma_indicator()
    data['EMA'] = ta.trend.EMAIndicator(data['Close'], window=20).ema_indicator()
    data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()
    macd = ta.trend.MACD(data['Close'])
    data['MACD'], data['MACD_Signal'], data['MACD_Hist'] = macd.macd(), macd.macd_signal(), macd.macd_diff()
    bbands = ta.volatility.BollingerBands(data['Close'])
    data['BB_High'], data['BB_Low'] = bbands.bollinger_hband(), bbands.bollinger_lband()
    so = ta.momentum.StochasticOscillator(data['High'], data['Low'], data['Close'])
    data['Stoch'], data['Stoch_Signal'] = so.stoch(), so.stoch_signal()
    ichimoku = ta.trend.IchimokuIndicator(data['High'], data['Low'])
    data['Ichimoku_A'], data['Ichimoku_B'], data['Ichimoku_Base'], data['Ichimoku_Conv'] = ichimoku.ichimoku_a(), ichimoku.ichimoku_b(), ichimoku.ichimoku_base_line(), ichimoku.ichimoku_conversion_line()
    data['Parabolic_SAR'] = ta.trend.PSARIndicator(data['High'], data['Low'], data['Close']).psar()
    data['OBV'] = ta.volume.OnBalanceVolumeIndicator(data['Close'], data['Volume']).on_balance_volume()
    return data

def calculate_fibonacci_retracement(data):
    max_price = data['High'].max()
    min_price = data['Low'].min()
    diff = max_price - min_price
    levels = [max_price - 0.236 * diff, max_price - 0.382 * diff, max_price - 0.5 * diff, max_price - 0.618 * diff, min_price]
    return levels

def calculate_fear_greed_index(data):
    rsi_normalized = (data['RSI'] - data['RSI'].min()) / (data['RSI'].max() - data['RSI'].min()) * 100
    sma_distance = data['Close'] / data['SMA'] - 1
    sma_normalized = (sma_distance - sma_distance.min()) / (sma_distance.max() - sma_distance.min()) * 100
    volume_normalized = (data['Volume'] - data['Volume'].min()) / (data['Volume'].max() - data['Volume'].min()) * 100
    fear_greed_index = (rsi_normalized + sma_normalized + volume_normalized) / 3
    return fear_greed_index

def plot_stock_data(data, ticker, indicators, fibonacci_levels, show_volume):
    fig = go.Figure()
    datetime_col = 'Datetime' if 'Datetime' in data.columns else 'Date'
    fig.add_trace(go.Candlestick(x=data[datetime_col], open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name='Candlesticks'))

    if 'SMA' in indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['SMA'], mode='lines', name='SMA', line=dict(color='orange')))
    if 'EMA' in indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['EMA'], mode='lines', name='EMA', line=dict(color='purple')))
    if 'BBands' in indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['BB_High'], mode='lines', name='BB High', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['BB_Low'], mode='lines', name='BB Low', line=dict(color='red')))
    if 'Ichimoku Cloud' in indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_A'], mode='lines', name='Ichimoku A', line=dict(color='pink')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_B'], mode='lines', name='Ichimoku B', line=dict(color='brown')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_Base'], mode='lines', name='Ichimoku Base Line', line=dict(color='yellow')))
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Ichimoku_Conv'], mode='lines', name='Ichimoku Conversion Line', line=dict(color='grey')))
    if 'Parabolic SAR' in indicators:
        fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Parabolic_SAR'], mode='markers', name='Parabolic SAR', marker=dict(color='green', symbol='circle', size=5)))

    for level in fibonacci_levels:
        fig.add_trace(go.Scatter(x=[data[datetime_col].iloc[0], data[datetime_col].iloc[-1]], y=[level, level], mode='lines', name=f'Fibonacci Level {level:.2f}', line=dict(dash='dash')))

    if show_volume:
        fig.add_trace(go.Bar(x=data[datetime_col], y=data['Volume'], name='Volume', marker=dict(color='gray'), yaxis='y2'))

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
    return fig

def plot_additional_charts(data, indicators):
    datetime_col = 'Datetime' if 'Datetime' in data.columns else 'Date'
    additional_fig = go.Figure()

    if 'RSI' in indicators:
        additional_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['RSI'], mode='lines', name='RSI', line=dict(color='blue')))
    if 'MACD' in indicators:
        additional_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD'], mode='lines', name='MACD', line=dict(color='blue')))
        additional_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['MACD_Signal'], mode='lines', name='MACD Signal', line=dict(color='red')))
        additional_fig.add_trace(go.Bar(x=data[datetime_col], y=data['MACD_Hist'], name='MACD Histogram'))
    if 'Stochastic Oscillator' in indicators:
        additional_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch'], mode='lines', name='Stochastic Oscillator', line=dict(color='blue')))
        additional_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['Stoch_Signal'], mode='lines', name='Stochastic Signal', line=dict(color='red')))
    if 'OBV' in indicators:
        additional_fig.add_trace(go.Scatter(x=data[datetime_col], y=data['OBV'], mode='lines', name='OBV', line=dict(color='blue')))

    additional_fig.update_layout(
        template='plotly_dark',
        xaxis_rangeslider_visible=False
    )
    return additional_fig

def plot_fear_greed_index(data):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=data['FearGreedIndex'].iloc[-1],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Fear and Greed Index"},
        gauge={
            'axis': {'range': [None, 100], 'tickvals': [0, 20, 40, 60, 80, 100], 'ticktext': ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']},
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
    return fig

@app.callback(
    [Output('stock-chart', 'figure'), Output('additional-charts', 'figure'), Output('fibonacci-levels', 'children'), Output('fear-greed-index', 'figure'), Output('options-chart', 'figure')],
    [Input('refresh-button', 'n_clicks'), Input('volume-threshold', 'value'), Input('oi-threshold', 'value')],
    [State('ticker-input', 'value'), State('time-frame-dropdown', 'value'), State('indicators-checklist', 'value')]
)
def update_charts(n_clicks, volume_threshold, oi_threshold, ticker, time_frame, indicators):
    interval = time_frame_mapping[time_frame]
    period = period_mapping[time_frame]
    data = load_data(ticker, period, interval)
    if data.empty:
        return {}, {}, "", {}, {}

    data = calculate_technical_indicators(data)
    fibonacci_levels = calculate_fibonacci_retracement(data)
    data['FearGreedIndex'] = calculate_fear_greed_index(data)

    stock_fig = plot_stock_data(data, ticker, indicators, fibonacci_levels, show_volume=True)
    additional_fig = plot_additional_charts(data, indicators)
    fear_greed_fig = plot_fear_greed_index(data)

    options_fig = options_data.display_options_data(ticker, volume_threshold, oi_threshold)

    fibonacci_levels_text = "Fibonacci Levels: " + ", ".join([f"{level:.2f}" for level in fibonacci_levels])

    return stock_fig, additional_fig, fibonacci_levels_text, fear_greed_fig, options_fig

if __name__ == '__main__':
    app.run_server(debug=True)
