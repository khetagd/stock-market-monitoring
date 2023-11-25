import webbrowser
import telebot
import pandas as pd
from telebot import types
import json
import requests

bot = telebot.TeleBot('6669067736:AAFld0-siHEvSVl8P3bhbHxh_GUPhV-uLVU')

#data = pd.read_csv('/Users/grigorij/Downloads/digital_currency_list.csv')
APIs = ['4JN9ZD24ZTMKWX5R', 'BHM7WHDX7K66ET61', '8OKWRXIXB7VBMGAP', 'ZG7VF29SB1BSCTVF', 'D9SOYTBRK9ULOSNP']

data = {}

@bot.message_handler(commands=['start'])
def main(message):
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Список доступных команд:')
    bot.send_message(message.chat.id, '/stock_info — получить информацию о стоимости валюты/акции/криптовалюты в долларах \n/add_stock — добавить валюту/акцию/криптовалюту в избранное')

@bot.message_handler(commands=['add_stock'])
def main(message):
    bot.send_message(message.chat.id, 'Введите название валюты.')
    bot.register_next_step_handler(message, add_stock)

def add_stock(message):
    try:
        data[str(message.chat.id)].append(message.text)
    except:
        data[str(message.chat.id)] = [message.text]
    df = pd.DataFrame(data)
    df.to_excel('/Users/khetag/Desktop/users_data.xlsx')
    bot.send_message(message.chat.id, f'{message.text} теперь в избранном.')

@bot.message_handler(commands=['stock_info'])
def main(message):
    bot.send_message(message.chat.id, 'Напишите название интересующей вас валюты.')
    bot.register_next_step_handler(message, get_stock_info)

def get_stock_info(message):
    currency = message.text.strip()
    curr_api_id = 0
    try:
        url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=USD&apikey={APIs[curr_api_id]}'
        res = requests.get(url)
        data = res.json()
        try:
            test = data['Information']
            curr_api_id += 1
            url = f'https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={currency}&to_currency=USD&apikey={APIs[curr_api_id]}'
            res = requests.get(url)
            data = res.json()
        except:
            pass
        curr_output = data["Realtime Currency Exchange Rate"]["4. To_Currency Name"]
        rate_output = data["Realtime Currency Exchange Rate"]["5. Exchange Rate"]
        bot.send_message(message.chat.id, f'Курс {currency} к {curr_output}: {rate_output}')
    except:
        try:
            url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={currency}&apikey={APIs[curr_api_id]}'
            res = requests.get(url)
            data = res.json()
            try:
                test = data['Information']
                curr_api_id += 1
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={currency}&apikey={APIs[curr_api_id]}'
                res = requests.get(url)
                data = res.json()
            except:
                pass
            curr_output = data["Global Quote"]["01. symbol"]
            rate_output = data["Global Quote"]["05. price"]
            bot.send_message(message.chat.id, f'Курс {curr_output} к доллару: {rate_output}')
        except:
            bot.send_message(message.chat.id, 'Что-то пошло не так :(')


bot.polling(none_stop=True)