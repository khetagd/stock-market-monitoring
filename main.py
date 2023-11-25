import webbrowser
import telebot
import pandas as pd
from telebot import types
import json
import requests
bot = telebot.TeleBot('6669067736:AAFld0-siHEvSVl8P3bhbHxh_GUPhV-uLVU')

#data = pd.read_csv('/Users/grigorij/Downloads/digital_currency_list.csv')
API = '4JN9ZD24ZTMKWX5R'


@bot.message_handler(commands=['start', 'hello'])
def main(message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}, напишите название интересующей вас валюты')
    bot.register_next_step_handler(message, get_security)


def get_security(message):
    currency = message.text.strip()
    url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=RUB&apikey=4JN9ZD24ZTMKWX5R'
    res = requests.get(url)
    data = res.json()
    curr_output = data["Realtime Currency Exchange Rate"]["4. To_Currency Name"]
    rate_output = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
    bot.send_message(message.chat.id, f'Курс {currency} к {curr_output}: {rate_output}')

@bot.message_handler(commands=['site'])
def site(message):
    webbrowser.open('https://www.cbr.ru/currency_base/daily/')




bot.polling(none_stop=True)
