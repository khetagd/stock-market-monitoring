import webbrowser
import telebot
import pandas as pd
from telebot import types
import sqlite3
bot = telebot.TeleBot('6669067736:AAFld0-siHEvSVl8P3bhbHxh_GUPhV-uLVU')

#data = pd.read_csv('/Users/grigorij/Downloads/digital_currency_list.csv')

#print(data['currency name'])

@bot.message_handler(commands=['start', 'hello'])
def main(message):
    connection = sqlite3.connect('users_info.sql')
    cur = connection.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users_info (id int auto_increment primary key,'
                ' user_id int, securities varchar(50))')
    connection.commit()
    cur.close()
    connection.close()
    markup = types.ReplyKeyboardMarkup()
    btn1 = 'Cайт с курсами валют'
    markup.row(btn1)
    btn2 = 'Доступные криптовалюты'
    markup.row(btn2)
    bot.send_message(message.chat.id, f'Здравствуйте, {message.from_user.first_name}, напишите название интересующей вас валюты', reply_markup=markup)
    bot.register_next_step_handler(message, on_click)  # функция которая сработает следующей вне зависимости от того что нажмут


def on_click(message):
    currency = message.text.strip()
    connection = sqlite3.connect('users_info.sql')
    cur = connection.cursor()
    cur.execute(f'INSERT INTO users_info (user_id, securities)'
                f' VALUES ({message.from_user.id}, {currency})')
    connection.commit()
    cur.close()
    connection.close()
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardMarkup('Список пользователей', callback_data = 'users'))
    bot.send_message(message.chat.id, 'Данные получены')

    if message.text == 'Доступные криптовалюты':
        data = pd.read_csv('/Users/grigorij/Downloads/digital_currency_list.csv')
        currencies = list(data["currency name"].unique())
        bot.send_message(message.chat.id, f'Список доступных криптовалют: {currencies[:len(currencies) // 2]}')
        bot.send_message(message.chat.id, f'{currencies[len(currencies) // 2:]}')

@bot.message_handler(commands=['site'])
def site(message):
    webbrowser.open('https://www.cbr.ru/currency_base/daily/')




bot.polling(none_stop=True)
