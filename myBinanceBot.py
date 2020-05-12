
#%% start

from binance.client import Client
import time
import matplotlib
from matplotlib import cm
import matplotlib.pyplot as plt
from binance.enums import *
import save_historical_data_Roibal
from myBinanceKeys import BinanceKey1
import mpl_finance
import pandas as pd
from datetime import datetime
import sched
import os.path
import numpy as np

api_key = BinanceKey1['api_key']
api_secret = BinanceKey1['api_secret']

client = Client(api_key, api_secret)

# get a deposit address for BTC
address = client.get_deposit_address(asset='BTC')

balance = {
    'EUR': 10000,
    'BTC': 0
}
symbol = 'BTCEUR'
bollinger_window = 20
start_timestamp = datetime.now()

last_index = None

def get_price_buy(base):
    depth = client.get_order_book(symbol=symbol)['asks']
    i = 0
    amount_coin = 0
    amount_base = base
    while amount_base > 0:
        price = float(depth[i][0])
        volume = float(depth[i][1])
        if price * volume > amount_base:
            amount_coin = amount_coin + amount_base / price
            amount_base = 0
        else:
            amount_coin += volume
            amount_base = amount_base - volume * price
        i += 1
    return base / amount_coin

def get_price_sell(coin):
    depth = client.get_order_book(symbol=symbol)['bids']
    i = 0
    amount_coin = coin
    amount_base = 0
    while amount_coin > 0:
        price = float(depth[i][0])
        volume = float(depth[i][1])
        if price * volume > amount_coin:
            amount_base = amount_base + amount_coin * price
            amount_coin = 0
        else:
            amount_base += volume * price
            amount_coin = amount_coin - volume
        i += 1
    return amount_base / coin


def run():
    data = get_data("3 hours ago UTC")
    save_data(data)

    #plot(data)
    s = sched.scheduler(time.time, time.sleep)
    #s.enter(30, 1, worker, (s, ))
    #s.enter(60, 2, plot_worker, (s, ))
    worker(s, 30)
    plot_worker(s, 600)
    s.run()

def worker(s, period):
    s.enter(period, 1, worker, (s, period))
    data = get_data("60 minutes ago UTC")
    save_data(data)
    last_row = data.iloc[-1]
    if last_row['Close'] < last_row['Lower Band']: 
        buy()
        #plot(data)
    if last_row['Close'] > last_row['Upper Band']: 
        sell()
        #plot(data)
    
def plot_worker(s, period):
    #data = get_data("3 hours ago UTC")
    data = pd.read_csv(
        '{}-{}.txt'.format(start_timestamp, symbol), 
        index_col='Time',
        dtype={
            'Time': 'str', 
            'Open': np.float64,
            'High': np.float64,
            'Low': np.float64,
            'Close': np.float64,
            'Volume': np.float64,
            'MA': np.float64,
            'STD': np.float64,
            'LowerBand': np.float64,
            'UpperBand': np.float64
        },
        parse_dates=['Time']
    )
    plot(data)
    s.enter(period, 2, plot_worker, (s, period))

def buy():
    global balance
    if balance['EUR'] > 0:
        #depth = client.get_order_book(symbol=symbol)
        #price = float(depth['asks'][0][0])
        price = get_price_buy(balance['EUR'])
        balance['BTC'] = (balance['EUR'] / price) * (1-0.001)
        balance['EUR'] = 0
        df = pd.DataFrame([{
            'Time': int(client.get_server_time()['serverTime']),
            'Price': price,
            'EUR': balance['EUR'],
            'BTC': balance['BTC']
        }])
        df.index = pd.to_datetime(df['Time'], unit='ms')
        filename = '{}-{}-buys.txt'.format(start_timestamp, symbol)
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False)
        else:
            df.to_csv(filename, mode='w', header=True)
        print('buying for {}'.format(price))
        print(balance)

def sell():
    global balance
    if balance['BTC'] > 0:
        #depth = client.get_order_book(symbol=symbol)
        #price = float(depth['bids'][0][0])
        price = get_price_sell(balance['BTC'])
        balance['EUR'] = (balance['BTC'] * price) * (1-0.001)
        balance['BTC'] = 0
        df = pd.DataFrame([{
            'Time': int(client.get_server_time()['serverTime']),
            'Price': price,
            'EUR': balance['EUR'],
            'BTC': balance['BTC']
        }])
        df.index = pd.to_datetime(df['Time'], unit='ms')
        filename = '{}-{}-sells.txt'.format(start_timestamp, symbol)
        if os.path.exists(filename):
            df.to_csv(filename, mode='a', header=False)
        else:
            df.to_csv(filename, mode='w', header=True)
        print('selling for {}'.format(price))
        print(balance)

def get_data(time_range):
    end = "now UTC"
    raw_data = save_historical_data_Roibal.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE, time_range, end)
    data = pd.DataFrame([{
        'Time': int(i[0]), 
        'Open': float(i[1]),
        'High': float(i[2]),
        'Low': float(i[3]),
        'Close': float(i[4]),
        'Volume': float(i[5])
        } for i in raw_data])
    data.index = pd.to_datetime(data['Time'], unit='ms')
    data['MA'] = data['Close'].rolling(window=bollinger_window).mean()
    data['STD'] = data['Close'].rolling(window=bollinger_window).std() 
    data['Upper Band'] = data['MA'] + (data['STD'] * 2)
    data['Lower Band'] = data['MA'] - (data['STD'] * 2)
    #print(data.dtypes)
    return data

def save_data(data):
    global last_index
    if not last_index:
        data.to_csv('{}-{}.txt'.format(start_timestamp, symbol), mode='a')
    else:
        data[data.index > last_index].to_csv('{}-{}.txt'.format(start_timestamp, symbol), mode='a', header = False)
    last_index = data.index[-1]

def plot(data):
    print(datetime.now())
    data[['Close', 'MA', 'Upper Band', 'Lower Band']].plot(figsize=(12,6))
    plt.title('{}'.format(symbol))
    plt.ylabel('Price')
    plt.show()

if __name__ == "__main__":
    run()

# %%
