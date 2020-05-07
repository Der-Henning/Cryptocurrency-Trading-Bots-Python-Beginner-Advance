
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

api_key = BinanceKey1['api_key']
api_secret = BinanceKey1['api_secret']

client = Client(api_key, api_secret)

# get a deposit address for BTC
address = client.get_deposit_address(asset='BTC')

def run():
    balance = {
        'EUR': 10000,
        'BTC': 0
    }
    symbol = 'BTCEUR'
    bollinger_window = 20
    start_timestamp = datetime.now()
    data = get_data(symbol, "3 hours ago UTC", bollinger_window)
    save_data(data,symbol,start_timestamp)
    plot(data, symbol)
    s = sched.scheduler(time.time, time.sleep)
    s.enter(10, 1, worker, (s, symbol, balance, bollinger_window))
    s.enter(600, 2, plot_worker, (s, symbol, bollinger_window))
    s.run()

def worker(s, symbol, balance, bollinger_window):
    s.enter(30, 1, worker, (s, symbol, balance, bollinger_window))
    data = get_data(symbol, "60 minutes ago UTC", bollinger_window)
    last_row = data.iloc[-1]
    if last_row['Close'] < last_row['Lower Band']: 
        buy(symbol)
        plot(data, symbol)
    if last_row['Close'] > last_row['Upper Band']: 
        sell(symbol)
        plot(data, symbol)
    
def plot_worker(s, symbol, bollinger_window):
    data = get_data(symbol, "3 hours ago UTC", bollinger_window)
    plot(data, symbol)
    s.enter(600, 2, plot_worker, (s, symbol, bollinger_window))

def buy(symbol):
    depth = client.get_order_book(symbol=symbol)
    price = depth['asks'][0][0]
    print('buying for {}'.format(price))

def sell(symbol):
    depth = client.get_order_book(symbol=symbol)
    price = depth['bids'][0][0]
    print('selling for {}'.format(price))

def get_data(symbol, time_range, bollinger_window):
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
    return data

def save_data(data, symbol, timestamp):
    data.to_csv('{}-{}.txt'.format(timestamp, symbol))

def plot(data, symbol):
    print(datetime.now())
    data[['Close', 'MA', 'Upper Band', 'Lower Band']].plot(figsize=(12,6))
    plt.title('{}'.format(symbol))
    plt.ylabel('Price')
    plt.show()



if __name__ == "__main__":
    run()

# %%
