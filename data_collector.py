from binance.client import Client
import time
import save_historical_data_Roibal
import pandas as pd
import pystore

def run():
    #data = get_data("BTCEUR", Client.KLINE_INTERVAL_1DAY, "01-01-2020", "05-10-2020")

    symbols = ["BTCEUR"]
    periods = [Client.KLINE_INTERVAL_1DAY,
        Client.KLINE_INTERVAL_1HOUR,
        Client.KLINE_INTERVAL_15MINUTE]
    years = [2018, 2020]

    pystore.set_path('./pystore')
    store = pystore.store('binance')

    #print(read_data("BTCUSDT", Client.KLINE_INTERVAL_15MINUTE))

    for symbol in symbols:
        collection = store.collection(symbol)
        for period in periods:
            data = get_data(symbol, 
                    period,
                    "01-01-{}".format(years[0]),
                    "12-31-{}".format(years[1]))
            if not data.empty:
                #print(data)
                
                collection.write(period, data, overwrite=True)

                print("saved {} {}".format(symbol, period))

def read_data(symbol, interval):
    pystore.set_path('./pystore')
    store = pystore.store('binance')
    collection = store.collection(symbol)
    data = collection.item(interval)

    return data.to_pandas()


def get_data(symbol, interval, start_str, end_str=None):
    #end = "now UTC"
    raw_data = save_historical_data_Roibal.get_historical_klines(symbol, interval, start_str, end_str)
    data = pd.DataFrame([{
        'Datetime': pd.to_datetime(int(i[0]), unit='ms'),
        'Timestamp': int(i[0]),
        'Open': float(i[1]),
        'High': float(i[2]),
        'Low': float(i[3]),
        'Close': float(i[4]),
        'Volume': float(i[5])
        } for i in raw_data])
    #print(data)
    #data.set_index('Timestamp')
    #if not data.empty:
        
        #data.index = pd.to_datetime(data['Timestamp'], unit='ms')
        #data.index.name = 'Datetime'
    return data

if __name__ == "__main__":
    run() 