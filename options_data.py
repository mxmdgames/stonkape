import yfinance as yf
import pandas as pd
from datetime import datetime
from dash import dcc, html
import plotly.graph_objects as go

def fetch_options_data(ticker, volume_threshold, oi_threshold):
    stock = yf.Ticker(ticker)
    options_expiration_dates = stock.options

    if not options_expiration_dates:
        return None, None

    all_calls = []
    all_puts = []

    for options_date in options_expiration_dates:
        options_chain = stock.option_chain(options_date)

        calls = options_chain.calls
        puts = options_chain.puts

        # Calculate DTE
        dte = (pd.to_datetime(options_date) - datetime.now()).days

        calls['DTE'] = f"{dte}DTE"
        puts['DTE'] = f"{dte}DTE"

        high_volume_calls = calls[(calls['volume'] >= volume_threshold) & (calls['openInterest'] >= oi_threshold)].copy()
        high_volume_puts = puts[(puts['volume'] >= volume_threshold) & (puts['openInterest'] >= oi_threshold)].copy()

        all_calls.append(high_volume_calls)
        all_puts.append(high_volume_puts)

    all_calls_df = pd.concat(all_calls)
    all_puts_df = pd.concat(all_puts)

    return all_calls_df, all_puts_df

def display_options_data(ticker, volume_threshold, oi_threshold):
    high_volume_calls, high_volume_puts = fetch_options_data(ticker, volume_threshold, oi_threshold)

    if high_volume_calls is None or high_volume_puts is None:
        return html.Div("No options data found for the given ticker.")

    calls_table = dcc.Graph(
        figure={
            'data': [go.Table(
                header=dict(values=list(high_volume_calls.columns),
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[high_volume_calls[col] for col in high_volume_calls.columns],
                           fill_color='lavender',
                           align='left'))
            ],
            'layout': go.Layout(title="High Volume Call Options")
        }
    )

    puts_table = dcc.Graph(
        figure={
            'data': [go.Table(
                header=dict(values=list(high_volume_puts.columns),
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[high_volume_puts[col] for col in high_volume_puts.columns],
                           fill_color='lavender',
                           align='left'))
            ],
            'layout': go.Layout(title="High Volume Put Options")
        }
    )

    return html.Div([calls_table, puts_table])

