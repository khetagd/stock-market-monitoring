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
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}! Список доступных команд:')
    bot.send_message(message.chat.id, '/stock_info — получить информацию о стоимости валюты/акции/криптовалюты в долларах \n/save_stock — добавить валюту/акцию/криптовалюту в избранное')

@bot.message_handler(commands=['save_stock'])
def main(message):
    bot.send_message(message.chat.id, 'Введите название валюты.')
    bot.register_next_step_handler(message, save_stock)

def save_stock(message):
    functions.SaveStock(message, bot, users_data)

@bot.message_handler(commands=['stock_info'])
def main(message):
    bot.send_message(message.chat.id, 'Напишите название интересующей вас валюты.')
    bot.register_next_step_handler(message, get_stock_info)

def get_stock_info(message):
    functions.GetStockInfo(message, bot)

bot.polling(none_stop=True)