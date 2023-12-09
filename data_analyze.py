import prophet
import datetime
import pandas as pd
from sktime.forecasting import arima # для работы arima надо установить библиотеку pdmarima
import logging 

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


def ProphetModel(data):
    try:
        predictor = prophet.Prophet() #создаем prophet модель
        predictor.fit(df = data[['date', 'open']].rename(columns ={'date':'ds','open':'y'})) # обучаем на прошлых значениях акции
        future = predictor.make_future_dataframe(periods=365) #прогнозируем в годовом масштабе
        forecast = predictor.predict(future) # получаем прогноз
        forecast = forecast.iloc[-365:0]
        forecast['weekday'] = forecast['ds'].apply(lambda x: x.weekday())
        forecast = forecast[(forecast['weekday'] != 5) & (forecast['weekday'] != 6)] # убираем из прогноза субботу и воскресенье (в эти дни не идет торговли акциями)
        return forecast.rename(columns = {'ds':'date'})[['date', 'y']]
    except Exception as e:
        analyze_logger.error(e, f'ProphetModel выкинул ошибку')
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
        return forecast[['date', 'y']]
    except Exception as e:
        analyze_logger.info(e, f'ArimaModel отработал')
        return data



