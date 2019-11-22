from telegram.ext import Updater
from settings import TG_TOKEN, TG_API_URL
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
import json

def sms(bot, update):
    print("'/start' was sent!")
    bot.message.reply_text("Hello, {}" .format(bot.message.chat.first_name))
    
    #pprint.pprint(bot.message)
    print(bot.message)
    #print(json.dumps(bot.message, indent=2))


def parrot(bot, update):
    print(bot.message.text)
    bot.message.reply_text(bot.message.text)

def main():
    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)

    my_bot.dispatcher.add_handler(CommandHandler('start',sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.text, parrot))


    my_bot.start_polling() #проверяет наличие сбщ с платформы тлг
    my_bot.idle() # бот работает пока его не остановят

    







main()