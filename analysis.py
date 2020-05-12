
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

import technical_indicators

from scipy.signal import savgol_filter

bollinger_window = 20

def run():
    
    data = pd.read_csv(
        '2020-05-07 14:57:53.506482-BTCEUR.txt',
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
    data['MA'] = data['Close'].rolling(window=bollinger_window).mean()
    data['STD'] = data['Close'].rolling(window=bollinger_window).std() 
    data['DIFF'] = data['Close'].diff()
    data['Upper Band'] = data['MA'] + (data['STD'] * 2)
    data['Lower Band'] = data['MA'] - (data['STD'] * 2)
    data['Savgol'] = savgol_filter(data['MA'], 59, 3)
    data['Savgol_Diff'] = data['Savgol'].diff()
    
    data = technical_indicators.relative_strength_index(data, bollinger_window)
    #print(data)
    #data['Savgol_Diff2'] = data['Savgol_Diff'].diff()
    #print(data)
    plot(data.loc[60:180])

    plot(data)

    #data[['RSI_59']].plot(figsize=(12,6))
    #close_filter = savgol_filter(data['Close'], 59, 3)
    #plt.plot(data.index, close_filter, figsize=(12,6))
    #plt.show()

    #data[['Savgol_Diff']].plot(figsize=(12,6))
    #data[['Savgol_Diff2']].plot(figsize=(12,6))


def plot(data, bollinger_window):
    print(datetime.now())

    fig, ax1 = plt.subplots(3, figsize=(30,12))
    ax1[0].set_xlabel('Datetime')
    ax1[0].set_ylabel('Price')
    ax1[0].plot(data['Datetime'], data['Close'])
    ax1[0].plot(data.index, data['MA'])
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
