import requests
import pandas as pd
import datetime
from dotenv import load_dotenv, find_dotenv
import os
import matplotlib.pyplot as plt
import argparse
import ast
load_dotenv(find_dotenv())

e2r={'binance':'USDT','bittrex':'USDT', 'kraken':'USD', 'upbit':'USDT', 'bitfinex':'USD', 'poloniex':'USDT',
     'hitbtc':'USDT', 'kucoin':'USDT', 'okex':'UDST', 'huobi':'USDT'}

def check_symbols(exchange):
    resp = requests.get(
        'https://rest-us-east-altcoinadvisors.coinapi.io/v1/symbols?filter_symbol_id={}'.format(exchange.upper()),
        {'apikey': os.environ.get('ALTCOIN_COINAPI_KEY')}).json()

    for symbolDict in resp:
        print(symbolDict['symbol_id'])

def view_time_period(exchange, market, startTime, endTime,loadCSV):
    marketSymSkeleton = '{}_SPOT_{}_{}'
    fileNameSkeleton = '{}_{}.csv'

    b, q = market.split('/')
    marketSym = marketSymSkeleton.format(exchange.upper(), b, q)

    print('Loading {} from {} to {}.'.format(marketSym, startTime, endTime))

    if (not loadCSV):
        startTime = datetime.datetime.strftime(startTime, '%Y-%m-%dT%H:%M:%SZ')
        endTime = datetime.datetime.strftime(endTime, '%Y-%m-%dT%H:%M:%SZ')

        resp = requests.get(
            'https://rest-us-east-altcoinadvisors.coinapi.io/v1/ohlcv/{}/history'.format(marketSym),
            {'apikey': os.environ.get('ALTCOIN_COINAPI_KEY'),
             'time_start': str(startTime), 'time_end': str(endTime), 'period_id': '1MIN'})
        print(resp)

        resp = resp.json()

        originalOHLCVDF = pd.DataFrame(data=resp)
        startTime = '_'.join(startTime.split(':'))
        fileName = fileNameSkeleton.format(marketSym, startTime)
        path = os.path.join('data', 'important_times', fileName)
        originalOHLCVDF.to_csv(path)
    else:
        startTime = datetime.datetime.strftime(startTime, '%Y-%m-%dT%H:%M:%SZ')
        startTime = '_'.join(startTime.split(':'))
        fileName = fileNameSkeleton.format(marketSym, startTime)
        path = os.path.join('data', 'important_times', fileName)
        originalOHLCVDF = pd.read_csv(path)

    originalOHLCVDF['time_close'] = pd.to_datetime(originalOHLCVDF['time_close'])
    originalOHLCVDF.set_index('time_close', inplace=True)

    originalOHLCVDF = originalOHLCVDF[['price_close', 'volume_traded']]
    originalOHLCVDF.plot(subplots=True)
    plt.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-exchange')
    parser.add_argument('-market', type=str)
    parser.add_argument('-startTime', type=str) #'2018-04-27 06:30:00'
    parser.add_argument('-endTime', type=str)
    parser.add_argument('-loadCSV', type=str)

    args = parser.parse_args()

    exchange = args.exchange
    market = args.market
    startTime = pd.Timestamp(args.startTime)
    endTime = pd.Timestamp(args.endTime)
    loadCSV = ast.literal_eval(args.loadCSV)

    view_time_period(exchange, market, startTime, endTime, loadCSV)
