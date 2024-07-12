import matplotlib.pyplot as plt
from pybit.unified_trading import HTTP
from config import api, secret
from talib import abstract
import time
import numpy as np

client = HTTP(
testnet=False, api_key=api,
api_secret=secret,
)

symbol = 'NEARUSDT'
threshold_percentage = 0.5
interval = 5

def get_klines (symbol):
    klines = client.get_kline(category='linear', symbol=symbol, interval=interval)
    klines = klines['result']['list']
    return klines

# print(get_klines(symbol, interval))

def get_close_data(klines) :
    close = [float(i[4]) for i in klines]
    close = close[:: -1]
    close = np. array(close)
    return close

# print(get_close_data(get_klines(symbol, interval)))

def get_sma(close) :
    SMA = abstract.Function('sma')
    data = SMA(close, timeperiod=25)
    # print(data)
    return data

# close = get_close_data(get_klines(symbol))
# data = get_sma(close)

def show_data ( ):
    # Построение графиков
    plt.figure(figsize=(14, 7))
    # График закрывающих цен
    plt.plot(close, label='Close Prices', color='blue')
    # График скользящей средней
    plt.plot(data, label='SMA 25', color='red')
    # plt. plot(smas, label='SMA 5', color='green')
    # Добавление заголовка и меток осей
    plt.title('Close Prices and SMA 25')
    plt.xlabel('Time')
    plt.ylabel('Price')

    # Легенда
    plt. legend()

    # Показ графика
    plt.show()

#show_data()

while True:
    close = get_close_data(get_klines(symbol))
    data = get_sma(close)
    last_close = close[-1]
    last_sma = data[-1]
    print(f'last_close: {last_close}, last_sma: {last_sma}')

    if last_sma is not None:
        deviation = abs((last_close - last_sma) / last_sma) * 100
        print(f"Deviation: {deviation}%")

        if deviation > threshold_percentage:
            if last_close > last_sma:
                print("Open Sell Order (short)")
                order = client.place_order(category='linear', symbol=symbol, side='Sell', orderType='Market', qty='2')
                print(order)

                while True:
                    close = get_close_data(get_klines(symbol))
                    data = get_sma(close)
                    last_close = close[-1]
                    last_sma = data[-1]
                    if last_close <= last_sma:
                        print("Open Buy Order (Close position)")
                        order = client.place_order(category='linear', symbol=symbol, side='Buy', orderType='Market', qty='2')
                        print(order)
                        break
                    else:
                        print("Watching the position")
                        print(f'last_close: {last_close}, last_sma: {last_sma}')
                        time.sleep(20)

            else:
                print("Open Buy Order (long)")
                order = client.place_order(category='linear', symbol=symbol, side='Buy', orderType='Market', qty='2')
                print(order)
                while True:
                    close = get_close_data(get_klines(symbol))
                    data = get_sma(close)
                    last_close = close[-1]
                    last_sma = data[-1]
                    if last_close >= last_sma:
                        print("Open Sell Order (Close position)")
                        order = client.place_order(category='linear', symbol=symbol, side='Sell', orderType='Market', qty='2')
                        print(order)
                        break
                    else:
                        print("Watching the position")
                        print(f'last_close: {last_close}, last_sma: {last_sma}')
                        time.sleep(20)
                break
        else:
            print("Insufficient data to calculate SMA")
            print(f"Sleep {interval} min")
            time.sleep(interval * 60)