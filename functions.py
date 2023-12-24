import pandas as pd
from telebot import types
import requests
import data_analyze
import matplotlib.pyplot as plt
import psycopg2
from io import BytesIO
from db import DataBase
from config import connection

db = DataBase(connection)

APIs = ['4JN9ZD24ZTMKWX5R', 'BHM7WHDX7K66ET61', '8OKWRXIXB7VBMGAP', 'ZG7VF29SB1BSCTVF',
        'D9SOYTBRK9ULOSNP']  # список токенов для подключения к API
curr_api_id = 0 # индекс токена, который используется в настоящий момент


def SaveStock(message: types.Message):  # сохраняем выбор акций, которые отслеживает пользователь
    tmp = message.text
    tmp1 = tmp.split(',')
    text = []
    for i in tmp1:
        text.append(i.strip().upper())
    db.add_data(message.from_user.id, text)
    

def GetStockInfo(message):  # запрашиваем базовую информацию о ценной бумаге
    currency = message.text.strip()  # currency - название акции
    global curr_api_id
    try:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=USD&apikey={APIs[curr_api_id]} '
        res = requests.get(url)  # запрос к api
        data = res.json()
        try:
            test = data['Information']  # второй запрос к api, на случай если токен исчерпал лимит
            curr_api_id += 1
            url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=USD&apikey={APIs[curr_api_id]}'
            res = requests.get(url)
            data = res.json()
        except:
            pass
        curr_output = data["Realtime Currency Exchange Rate"]["1. From_Currency Code"]
        rate_output = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        return curr_output, rate_output
    except:
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={currency}&apikey={APIs[curr_api_id]}'
            res = requests.get(url)
            data = res.json()
            try:
                test = data['Information'] # тут все аналогично предыдущему блоку try - except
                curr_api_id += 1
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={currency}&apikey={APIs[curr_api_id]}'
                res = requests.get(url)
                data = res.json()
            except:
                pass
            curr_output = data["Global Quote"]["01. symbol"]
            rate_output = data["Global Quote"]["05. price"]
            return curr_output, rate_output
        except:
            return -1, -1


def GetHistoricalData(message):  # получение исторических значений акций
    currency = message.text.strip().split()[0]  # currency - название акции
    global curr_api_id
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={currency}&apikey={APIs[curr_api_id]}&outputsize=full'
    r = requests.get(url)
    data = r.json()

    try:
        test = data['Information']
        curr_api_id += 1
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={currency}&apikey={APIs[curr_api_id]}&outputsize=full'
        res = requests.get(url)
        data = res.json()
    except:
        pass

    data = dict(data['Time Series (Daily)'])
    data = pd.DataFrame().from_dict(data, orient='index')  # преобразуем данные из json в pandas

    return data


def GetMonthlyData(message):  # получение месячных данных по акции
    data = GetHistoricalData(message).iloc[0:30]
    return data


def GetYearData(message):  # получение годовых данных по акции
    data = GetHistoricalData(message).iloc[0:365]
    return data
    
def GetSMAData(message):  # получение скользящей средней для акции с заданным интервалом: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
    currency = message.text.strip().split()[0]  # currency - название акции
    interval = message.text.strip().split()[1]
    global curr_api_id
    url = f'https://www.alphavantage.co/query?function=SMA&symbol={currency}&interval={interval}&time_period=10&series_type=open&apikey={APIs[curr_api_id]}'
    r = requests.get(url)
    data = r.json()

    try:
        test = data['Information']
        curr_api_id += 1
        url = f'https://www.alphavantage.co/query?function=SMA&symbol={currency}&interval={interval}&time_period=10&series_type=open&apikey={APIs[curr_api_id]}'
        res = requests.get(url)
        data = res.json()
    except:
        pass
    data = dict(data['Technical Analysis: SMA'])
    data = pd.DataFrame().from_dict(data, orient='index')  # преобразуем данные из json в pandas

    return data

def GetRSIData(message): # получение RSI для акции с заданным интервалом: 1min, 5min, 15min, 30min, 60min, daily, weekly, monthly
    currency = message.text.strip().split()[0]  # currency - название акции
    interval = message.text.strip().split()[1]
    global curr_api_id
    url = f'https://www.alphavantage.co/query?function=RSI&symbol={currency}&interval={interval}&time_period=10&series_type=open&apikey={APIs[curr_api_id]}'
    r = requests.get(url)
    data = r.json()

    try:
        test = data['Information']
        curr_api_id += 1
        url = f'https://www.alphavantage.co/query?function=RSI&symbol={currency}&interval={interval}&time_period=10&series_type=open&apikey={APIs[curr_api_id]}'
        res = requests.get(url)
        data = res.json()
    except:
        pass
    data = dict(data['Technical Analysis: RSI'])
    data = pd.DataFrame().from_dict(data, orient='index')  # преобразуем данные из json в pandas
    return data


def GetForecast(message): # возвращает предсказания, построенные моделями ARIMA и Prophet
    try:
        data = GetHistoricalData(message)
        ar= data_analyze.GetModels(data)
        return ar
    except:
        return -1

def GetSMAGraph(message): # возвращает график для SMA выбранной акции
    try:
        interval = message.text.strip().split()[1]
        data = GetSMAData(message)
        if interval == 'daily':
            fig = data_analyze.SMAGraphMonth(data, message.text.strip().split()[0])
        else:
            fig = data_analyze.SMAGraph24Hours(data, message.text.strip().split()[0])
        # plt.savefig() вот тут ты должен сохранить где-то этот график и выдать пользователю потом
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        return buffer
    except:
        return -1
    
def GetRSIGraph(message): # возвращает график для RSI выбранной акции
    try:
        interval = message.text.strip().split()[1]
        data = GetRSIData(message)
        if interval == 'daily':
            fig = data_analyze.RSIGraphMonth(data, message.text.strip().split()[0])
        else:
            fig = data_analyze.RSIGraph24Hours(data, message.text.strip().split()[0])
        # plt.savefig() вот тут ты должен сохранить где-то этот график и выдать пользователю потом
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        return buffer
    except:
        return -1
    
def GetCandleGraph(message):
    try:
        interval = message.text.strip().split()[1]
        data = GetHistoricalData(message)

        buffer = data_analyze.CandleGraph(data, interval)
        
        return buffer
    except:
        return -1



def GetMorningEveningStars(message): # возвращает списки утренних и вечерних звезд
    try:
        data = GetYearData(message)
        prework_data = data_analyze.DataPreWork(data)
        mornings = data_analyze.MorningStar(prework_data)
        evenings = data_analyze.EveningStar(prework_data)
        return mornings, evenings
    except:
        return -1, -1
