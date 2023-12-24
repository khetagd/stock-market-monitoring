import webbrowser
import telebot
import pandas as pd
from telebot import types
import json
import requests
import functions
import data_analyze
from db import DataBase
from config import connection
from PIL import Image


db = DataBase(connection)

bot = telebot.TeleBot('6669067736:AAFld0-siHEvSVl8P3bhbHxh_GUPhV-uLVU')

data_analyze.StartLogger() # запускаем логгер

@bot.message_handler(commands=['start']) # функция, выводящая приветствие и основную информацию о коммандах
def main(message: types.Message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Список доступных команд: \n\n/stock_price — получить информацию о стоимости валюты/акции/криптовалюты в долларах \n\n/save_stock — добавить валюту/акцию/криптовалюту в избранное \n\n/get_sma — получить графическое представление SMA выбранной акции\n\n/forecast — получить предсказание процентного изменения стоимости выбранной акции\n\n/get_stars — получить список утренних и вечерних звезд за год\n\n/get_rsi — получить график RSI выбранной акции\n\n/get_candles — получить график свеч выбранной акции')
    db.check_user(message.from_user.id) # сразу проверяем есть ли позователь в базе и если что добавляем его




@bot.message_handler(commands=['save_stock']) # функция, сохраняющая предпочения пользователя
def main(message):
    bot.send_message(message.chat.id, f'Введите тикер акции/криптовалюты.\nЕсли хотите добавить несколько, перечислите их через запятую\nНапример: ticker1, ticker2')
    bot.register_next_step_handler(message, save_stock)

def save_stock(message):
    functions.SaveStock(message)
    bot.send_message(message.chat.id, f'{message.text} теперь в избранном.')





@bot.message_handler(commands=['stock_price']) # функция, возвращающая стоимость запрошенной акции или криптовалюты
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции/криптовалюты.')
    bot.register_next_step_handler(message, get_stock_info)

def get_stock_info(message):
    curr_output, rate_output = functions.GetStockInfo(message)
    if curr_output != -1:
        bot.send_message(message.chat.id, f'Курс {curr_output} к доллару: {rate_output}')
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так :(')




@bot.message_handler(commands=['get_sma']) # функция, возвращающая график SMA выбранной акции
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции и выберите интервал (1min, daily). Например: AAPL 1min')
    bot.register_next_step_handler(message, get_sma_graph)

def get_sma_graph(message):
    data = functions.GetSMAGraph(message)
    
    if data != -1:
        bot.send_photo(message.chat.id, photo=data)
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так :(')




@bot.message_handler(commands=['get_rsi']) # функция, возвращающая график RSI выбранной акции
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции и выберите интервал (1min, daily). Например: AAPL 1min')
    bot.register_next_step_handler(message, get_rsi_graph)

def get_rsi_graph(message):
    data = functions.GetRSIGraph(message)
    
    if data != -1:
        bot.send_photo(message.chat.id, photo=data)
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так :(')

@bot.message_handler(commands=['forecast']) # функция, выводящая предсказание для выбранной акции или криптовалюты
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции/криптовалюты.')
    bot.register_next_step_handler(message, get_forecast)

def get_forecast(message):
    bot.send_message(message.chat.id, 'Пожалуйста, ожидайте, время анализа может доходить до нескольких минут.')
    res_arima = functions.GetForecast(message)
    if res_arima != -1:
        bot.send_message(message.chat.id, f'Процентное изменение, предсказанное моделью ARIMA: {res_arima}')
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так :(')





@bot.message_handler(commands=['get_stars']) # функция, выводящая утренние и вечерние звезд, возвращает список дат
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции/криптовалюты.')
    bot.register_next_step_handler(message, get_stars)

def get_stars(message):
    if morning != -1:
        morning, evening = functions.GetMorningEveningStars(message)
        bot.send_message(message.chat.id, f'Утренние: {morning}\n\nВечерние: {evening}')
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так :(')
    

bot.polling(none_stop=True)
