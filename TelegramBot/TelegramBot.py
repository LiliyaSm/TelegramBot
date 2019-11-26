from telegram.ext import Updater
from settings import TG_TOKEN, TG_API_URL
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler
from telegram.ext import Filters
import json
import csv
import re
from database import mydatabase
from handlers import *


def main():

    dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mydb.sqlite')
    # Create Tables
    #dbms.create_db_tables()

    # dbms.insert_single_data()
    # dbms.print_all_data(mydatabase.USERS)


    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)

    my_bot.dispatcher.add_handler(CommandHandler('start', sms))
    my_bot.dispatcher.add_handler(MessageHandler(Filters.regex("Мои подписки"), subscription))

    expression = r'(^https://[a-z]{2,3}.avito.ru/.*)'
    # my_bot.dispatcher.add_handler(
    # MessageHandler(Filters.regex(expression), pars))

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex("Установить наблюдение"), start_observation)],
                            allow_reentry = True,
                            states={
                                "link": [MessageHandler(Filters.regex(expression), pars),
                                        MessageHandler(Filters.regex("Отмена"), answer_no),
                                         MessageHandler(Filters.text, not_link)],
                                "confirm": [MessageHandler(Filters.regex("Да"), answer_yes),
                                            MessageHandler(
                                                Filters.regex("Нет"), answer_no)
                                            ]
        },
            fallbacks=[MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, donot_know)]
        )
    )
    

    my_bot.dispatcher.add_handler(MessageHandler(Filters.text | Filters.video | Filters.photo | Filters.document, donot_know))
    my_bot.start_polling()  # проверяет наличие сбщ с платформы тлг
    my_bot.idle()  # бот работает пока его не остановят


if __name__ == '__main__':
    main()
