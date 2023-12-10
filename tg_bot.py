import webbrowser
import telebot
import pandas as pd
from telebot import types
import json
import requests
import functions

bot = telebot.TeleBot('6669067736:AAFld0-siHEvSVl8P3bhbHxh_GUPhV-uLVU')

#data = pd.read_csv('/Users/grigorij/Downloads/digital_currency_list.csv')

users_data = {}

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Список доступных команд: \n\n/stock_price — получить информацию о стоимости валюты/акции/криптовалюты в долларах \n\n/save_stock — добавить валюту/акцию/криптовалюту в избранное \n\n/get_sma — получить графическое представление SMA выбранной акции\n\n/forecast — получить предсказание процентного изменения стоимости выбранной акции')

@bot.message_handler(commands=['save_stock'])
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер акции/криптовалюты.')
    bot.register_next_step_handler(message, save_stock)

def save_stock(message):
    functions.SaveStock(message, users_data)
    bot.send_message(message.chat.id, f'{message.text} теперь в избранном.')

@bot.message_handler(commands=['stock_price'])
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции/криптовалюты.')
    bot.register_next_step_handler(message, get_stock_info)

def get_stock_info(message):
    curr_output, rate_output = functions.GetStockInfo(message)
    if curr_output != -1:
        bot.send_message(message.chat.id, f'Курс {curr_output} к доллару: {rate_output}')
    else:
        bot.send_message(message.chat.id, 'Что-то пошло не так :(')

@bot.message_handler(commands=['get_sma'])
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции/криптовалюты и выберите интервал (1min, daily).')
    bot.register_next_step_handler(message, get_sma_graph)

def get_sma_graph(message):
    data = functions.GetSMAGraph(message)
    bot.send_photo(message.chat.id, photo=data)

@bot.message_handler(commands=['forecast'])
def main(message):
    bot.send_message(message.chat.id, 'Введите тикер интересующей вас акции/криптовалюты.')
    bot.register_next_step_handler(message, get_forecast)

def get_forecast(message):
    bot.send_message(message.chat.id, 'Пожалуйста, ожидайте, время анализа может доходить до нескольких минут.')
    res_arima, res_prophet = functions.GetForecast(message)
    bot.send_message(message.chat.id, f'Процентное изменение, предсказанное моделью ARIMA: {res_arima}\n\nПроцентное изменение, предсказанное моделью Prophet: {res_prophet}')

bot.polling(none_stop=True)
