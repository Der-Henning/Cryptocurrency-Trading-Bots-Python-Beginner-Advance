#%%

from binance.client import Client
import time
#import save_historical_data_Roibal
import pandas as pd
import data_collector
import technical_indicators
from datetime import datetime
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta

def run():
    symbol = "BTCUSDT"
    start_fiat = 10000

    balance = {
        'fiat': start_fiat,
        'coin': 0
    }

    data = bot1(symbol, balance)

    print(balance)
    rendite = (balance['fiat'] / start_fiat - 1) * 100
    diff = data.iloc[-1]['Datetime'] - data.iloc[0]['Datetime']
    rendite_pa = rendite * 365 / diff.days
    print('Rendite: {}%'.format(rendite))
    print('Rendite p.a.: {}%'.format(rendite_pa))


def bot1(symbol, balance):
    interval = Client.KLINE_INTERVAL_15MINUTE
    bollinger_window = 30

    def plot(data, pair):
        fig, ax1 = plt.subplots(2, figsize=(12,6))
        ax1[0].set_xlabel('Datetime')
        ax1[0].set_ylabel('Price')
        ax1[0].plot(data['Datetime'], data['Close'])
        ax1[0].plot(data['Datetime'], data['MA'])
        ax1[0].plot(data['Datetime'], data['Upper Band'])
        ax1[0].plot(data['Datetime'], data['Lower Band'])
        ax1[0].axvline(data['Datetime'][pair[0]])
        ax1[0].axvline(data['Datetime'][pair[1]])

        ax1[1].plot(data['Datetime'], data['RSI_{}'.format(bollinger_window)])
        ax1[1].axhline(0.7, ls='--')
        ax1[1].axhline(0.3, ls='--')
        ax1[1].set_ylim(0, 1)
        ax1[1].set_ylabel('RSI')
        ax1[1].axvline(data['Datetime'][pair[0]])
        ax1[1].axvline(data['Datetime'][pair[1]])

        plt.show()

    data = data_collector.read_data(symbol, interval)
    data['MA'] = data['Close'].rolling(window=bollinger_window).mean()
    data['STD'] = data['Close'].rolling(window=bollinger_window).std() 
    data['Upper Band'] = data['MA'] + (data['STD'] * 2)
    data['Lower Band'] = data['MA'] - (data['STD'] * 2)
    data = technical_indicators.relative_strength_index(data, bollinger_window)

    trade_pairs = []
    buy_index = 0
    for index, row in data.iloc[bollinger_window:].iterrows():
        if row['Close'] < row['Lower Band'] and row['RSI_{}'.format(bollinger_window)] < 0.3:
            if buy(balance, get_price(data, index), row['Datetime']):
                buy_index = index

        if row['Close'] > row['Upper Band'] and row['RSI_{}'.format(bollinger_window)] > 0.7:
            if sell(balance, get_price(data, index), row['Datetime']):
                trade_pairs.append([buy_index, index])
            
    if sell(balance, get_price(data, index), row['Datetime']):
        trade_pairs.append([buy_index, index])

    for pair in trade_pairs:
        start = pair[0] - 10 if pair[0] - 10 >= 0 else 0
        end = pair[1] + 10 if pair[1] + 10 <= data.tail(1).index.item() else data.tail(1).index.item()

        plot(data[start:end], pair)
        print("Rendite: {}%".format((data['Close'][pair[1]] / data['Close'][pair[0]] - 1) * 100))

    return data

def run_old():
    interval = Client.KLINE_INTERVAL_15MINUTE
    symbol = "BTCEUR"
    start = "01-01-2020"
    end = "05-10-2020"
    bollinger_window = 30

    data = data_collector.get_data(symbol, interval, start, end)
    data['MA'] = data['Close'].rolling(window=bollinger_window).mean()
    data['STD'] = data['Close'].rolling(window=bollinger_window).std() 
    data['Upper Band'] = data['MA'] + (data['STD'] * 2)
    data['Lower Band'] = data['MA'] - (data['STD'] * 2)
    data = technical_indicators.relative_strength_index(data, bollinger_window)

    #difference_in_years = relativedelta(data.iloc[-1]['Datetime'], data.iloc[0]['Datetime'])
  

    #print(data)
    #plot(data, bollinger_window)

    #print(data.iloc[bollinger_window:])

    start_eur = 10000

    balance = {
        'EUR': start_eur,
        'BTC': 0
    }

    #### macd

    bollinger_u = False
    bollinger_l = False
    RSI_u = False
    RSI_l = False
    stop_loss = 0

    for index, row in data.iloc[bollinger_window:].iterrows():
        
        bollinger_u = True if row['Close'] > row['Upper Band'] else False
        bollinger_l = True if row['Close'] > row['Lower Band'] else False

        if (bollinger_u and RSI_u and row['RSI_{}'.format(bollinger_window)] < 0.7) or row['Close'] < stop_loss:
            sell(balance, get_price(data, index), row['Datetime'])
            stop_loss = 0

        if bollinger_l and RSI_l and row['RSI_{}'.format(bollinger_window)] > 0.3:
            buy(balance, get_price(data, index), row['Datetime'])
            stop_loss = row['Close'] * 0.95

        RSI_u = True if row['RSI_{}'.format(bollinger_window)] > 0.7 else False
        RSI_l = True if row['RSI_{}'.format(bollinger_window)] < 0.3 else False
    
    sell(balance, data.iloc[-1]['Close'], data.iloc[-1]['Datetime'])
    print(balance)
    rendite = (balance['EUR'] / start_eur - 1) * 100
    diff = data.iloc[-1]['Datetime'] - data.iloc[0]['Datetime']
    rendite_pa = rendite * 365 / diff.days
    print('Rendite: {}%'.format(rendite))
    print('Rendite p.a.: {}%'.format(rendite_pa))

def get_price(data, index):
    if index + 1 in data.index:
        return data.iloc[index + 1]['Open']
    else:
        return data.iloc[index]['Close']

def buy(balance, price, date):
    if balance['fiat'] > 0:
        balance['coin'] = (balance['fiat'] / price) * (1-0.001)
        balance['fiat'] = 0
        print('{} buy at {} \t {}'.format(date, price, balance))
        return True
    return False

def sell(balance, price, date):
    if balance['coin'] > 0:
        balance['fiat'] = (balance['coin'] * price) * (1-0.001)
        balance['coin'] = 0
        print('{} sell at {} \t {}'.format(date, price, balance))
        return True
    return False

def plot(data, bollinger_window):
    print(datetime.now())

    fig, ax1 = plt.subplots(3, figsize=(120,12))
    ax1[0].set_xlabel('Datetime')
    ax1[0].set_ylabel('Price')
    ax1[0].plot(data['Datetime'], data['Close'])
    ax1[0].plot(data['Datetime'], data['MA'])
    ax1[0].plot(data['Datetime'], data['Upper Band'])
    ax1[0].plot(data['Datetime'], data['Lower Band'])
    #ax1[0].plot(data['Datetime'], data['Savgol'])
    
    #ax2 = ax1[0].twinx()

    #ax2.set_ylabel('diff')
    #ax2.plot(data['Time'], data['RSI_{}'.format(bollinger_window)], color='black')
    ax1[1].plot(data['Datetime'], data['RSI_{}'.format(bollinger_window)])
    ax1[1].axhline(0.7, ls='--')
    ax1[1].axhline(0.3, ls='--')
    ax1[1].set_ylim(0, 1)
    ax1[1].set_ylabel('RSI')

    ax1[2].plot(data['Datetime'], data['Volume'])
    ax1[2].set_ylabel('Volume')
    #data[['Close', 'MA', 'Upper Band', 'Lower Band', 'Savgol']].plot(figsize=(12,6))
    #plt.title('{}'.format(symbol))
    #plt.ylabel('Price')
    plt.show()

if __name__ == "__main__":
    run() 

# %%
