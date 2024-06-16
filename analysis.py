import pandas as pd

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
def identify_support_resistance(data, datetime_col='Date'):
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
