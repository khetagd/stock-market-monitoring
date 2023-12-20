import prophet
import datetime
import pandas as pd
from sktime.forecasting import arima # для работы arima надо установить библиотеку pdmarima
import logging 
from talib import abstract
import matplotlib.pyplot as plt 
import seaborn as sns
from io import BytesIO
import mplfinance as mpf

def StartLogger():
    analyze_logger = logging.getLogger('analyze_logger')
    analyze_logger.setLevel(logging.DEBUG) 
    handler_for_error = logging.FileHandler("errors.log", mode='w')
    handler_for_error.setLevel(logging.ERROR) # Инициализация handler'a
    handler_for_error.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)s %(message)s", "%Y-%m-%d %H:%M:%S"))
    analyze_logger.addHandler(handler_for_error)

def DataPreWork(data):
    try:
        for column in data.columns:
            data[column] = data[column].apply(lambda x: float(x)) #меняем тип данных значений акций на числовой
        data = data.reset_index().rename(columns = {'index':'date', '1. open':'open', '2. high':'high', '3. low':'low', '4. close':'close', '5. volume':'volume'}) #чуть подредактировали названия колонок
        data['date'] = data['date'].apply(lambda x: datetime.datetime.fromisoformat(x)) #меняем тип данных дат на datetime
        return data
    except Exception as e:
        analyze_logger.error(e, f'DataPreWork выкинул ошибку')
        return data


def ArimaModel(data):
    try:
        predictor = arima.AutoARIMA() #создаем arima модель
        predictor.fit(data[::-1][['date', 'open']].rename(columns ={'date':'ds','open':'y'}).reset_index().drop(columns=['index'])) #переворачиваем данные по дате, чтобы обучить модель
        forecast = predictor.predict(list(range(0,366))) #пытаемся предугадать годовые значения
        forecast = forecast.reset_index().drop(columns = ['index'])
        forecast['date'] = forecast.index
        start_date = data.date.iloc[0]
        forecast.date = forecast.date.apply(lambda x: start_date + datetime.timedelta(x + 1)) #добавляем дату
        forecast['weekday'] = forecast['date'].apply(lambda x: x.weekday())
        forecast = forecast[(forecast['weekday'] != 5) & (forecast['weekday'] != 6)] # убираем из прогноза субботу и воскресенье (в эти дни не идет торговли акциями)
        return forecast.reset_index()[['date', 'y']]
    except Exception as e:
        analyze_logger.error(e, f'ArimaModel выкинул ошибку')
        return data
    


def GetModels(data): #функция которая запускает обе модели и выдает результат через год
    prework_data = DataPreWork(data)
    today_value = prework_data.iloc[0].open #текущее значение акции 
    arima_data = ArimaModel(prework_data)
    arima_result = (arima_data.iloc[-1].y - today_value)/today_value #относительное изменение стоимости (arima)
    return 100*arima_result


def SMAGraph24Hours(sma_data, stock_name): #строим график плавающей средней акции за последние сутки
    sma_data = sma_data.reset_index().rename(columns = {'index':'date'})
    sma_data.SMA = sma_data.SMA.apply(lambda x: float(x)) #меняем тип SMA на float
    sma_data.date = sma_data.date.apply(lambda x: datetime.datetime.fromisoformat(x)) #ставим datetime для даты
    sma_data = sma_data.iloc[-60*24:]
    fig = plt.figure(figsize=(10, 5)) #создаем график
    sns.lineplot(data = sma_data, x = 'date', y = 'SMA')
    plt.title(f'{stock_name} SMA')
    return fig


def SMAGraphMonth(sma_data, stock_name): #строим график плавающей средней акции за последний месяц
    sma_data = sma_data.reset_index().rename(columns = {'index':'date'})
    sma_data.SMA = sma_data.SMA.apply(lambda x: float(x)) #меняем тип SMA на float
    sma_data.date = sma_data.date.apply(lambda x: datetime.datetime.fromisoformat(x)) #ставим datetime для даты
    sma_data = sma_data.iloc[-30:]
    fig = plt.figure(figsize=(10, 5)) #создаем график
    sns.lineplot(data = sma_data, x = 'date', y = 'SMA')
    plt.title(f'{stock_name} SMA')
    return fig


def MorningStar(data): #ищем для пользователя фигуры утренние звезды (трейдинг)
    new_data = data[::-1].reset_index().drop(columns = ['index'])
    new_data = new_data.reset_index()
    MS = abstract.CDLMORNINGSTAR(new_data) #функция из talib
    MS = MS.reset_index().rename(columns = {0:'MS'})
    MS = MS[MS.MS != 0]
    return list(pd.merge(MS, new_data).date.apply(lambda x: str(x.date()))) #возвращаем список дат, когда были утренние звезды


def EveningStar(data): #ищем для пользователя фигуры вечерние звезды (трейдинг)
    new_data = data[::-1].reset_index().drop(columns = ['index'])
    new_data = new_data.reset_index()
    ES = abstract.CDLEVENINGSTAR(new_data) #функция из talib
    ES = ES.reset_index().rename(columns = {0:'ES'})
    ES = ES[ES.ES != 0]
    return list(pd.merge(ES, new_data).date.apply(lambda x: str(x.date()))) #возвращаем список дат, когда были вечерние звезды


def CandleGraph(data, days): #рисует свечной график, за сколько дней
    for column in data.columns:
        data[column] = data[column].apply(lambda x: float(x))
    data = data.rename(columns = {'1. open':'open', '2. high':'high', '3. low':'low', '4. close':'close', '5. volume':'volume'})
    data.index = pd.DatetimeIndex(data.index)
    buffer = BytesIO()
    save = dict(fname=buffer, dpi=100, pad_inches=0.25)
    buffer.seek(0)
    if days < len(data): 
        mpf.plot(data.iloc[:days], type='candle', style='charles',
                title='Свечной график',
                ylabel='Цена ($)', savefig = save)
    else:
        mpf.plot(data, type='candle', style='charles',
                title='Свечной график',
                ylabel='Цена ($)', savefig = save)
    return buffer


def RSIGraph24Hours(rsi_data, stock_name): #строим график RSI за последние сутки
    rsi_data = rsi_data.reset_index().rename(columns = {'index':'date'})
    rsi_data.RSI = rsi_data.RSI.apply(lambda x: float(x)) #меняем тип RSI на float
    rsi_data.date = rsi_data.date.apply(lambda x: datetime.datetime.fromisoformat(x)) #ставим datetime для даты
    fig = plt.figure(figsize=(10, 5))
    sns.lineplot(data = rsi_data[:-24*60:-1], x = 'date', y = 'RSI')
    plt.axhline(70, color='red', linestyle='dashed') # Линия перекупленности
    plt.axhline(30, color='green', linestyle='dashed') # Линия перепроданности
    plt.title(f'{stock_name} RSI')

def RSIGraphMonth(rsi_data, stock_name): #строим график плавающей средней акции за последний месяц
    rsi_data = rsi_data.reset_index().rename(columns = {'index':'date'})
    rsi_data.RSI = rsi_data.RSI.apply(lambda x: float(x)) #меняем тип RSI на float
    rsi_data.date = rsi_data.date.apply(lambda x: datetime.datetime.fromisoformat(x)) #ставим datetime для даты
    fig = plt.figure(figsize=(10, 5))
    sns.lineplot(data = rsi_data[:-30:-1], x = 'date', y = 'RSI')
    plt.axhline(70, color='red', linestyle='dashed') # Линия перекупленности
    plt.axhline(30, color='green', linestyle='dashed') # Линия перепроданности
    plt.title(f'{stock_name} RSI')
