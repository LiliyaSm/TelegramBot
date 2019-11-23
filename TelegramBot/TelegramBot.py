from telegram.ext import Updater
from settings import TG_TOKEN, TG_API_URL
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram import ReplyKeyboardMarkup
import json
import requests
from bs4 import BeautifulSoup
import csv
import re
from database import mydatabase



def sms(bot, update):
    print("'/start' was sent!")
    my_keyboard = ReplyKeyboardMarkup([["/start"], ["Установить наблюдение"]],  resize_keyboard=True) #добавляем кнопки
    bot.message.reply_text("Приветствую, {}. Нажимай на кнопку".format(bot.message.chat.first_name), reply_markup = my_keyboard)
    
    #pprint.pprint(bot.message)
    print(bot.message)
    #print(json.dumps(bot.message, indent=2))


def get_html(url):
    r = requests.get(url)
    return r.text

def pars(bot, update):
    print("link was sent!")
    html = get_html(bot.message.text)    # сообщение из чата
    soup = BeautifulSoup(html, 'lxml') 
    
    try:
        price = soup.find('span', class_ ='js-item-price').text
    except:
        bot.message.reply_text("цена на странице не найдена :(")

    print(price)    
    bot.message.reply_text("Цена товара: " + price)    
    return price


def parrot(bot, update):
    print(bot.message.text)
    bot.message.reply_text("это не ссылка!")

def main():

    dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mydb.sqlite')
    # Create Tables
    #dbms.create_db_tables()

    # dbms.insert_single_data()
    #dbms.print_all_data(mydatabase.USERS)

    #dbms.sample_query() # simple query
    #dbms.sample_delete() # delete data
    #dbms.sample_insert() # insert data
    #dbms.sample_update() # update data

    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)

    my_bot.dispatcher.add_handler(CommandHandler('start',sms))
    
    expression = r'(^https:\/\/[a-z]{2,3}\.avito\.ru\/.*)'
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex(expression), pars))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))
    my_bot.start_polling() #проверяет наличие сбщ с платформы тлг
    my_bot.idle() # бот работает пока его не остановят

    


main()
#Filters.regex(expression)


#?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)