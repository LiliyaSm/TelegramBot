from telegram.ext import Updater
from settings import TG_TOKEN, TG_API_URL
from telegram.ext import CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton
from telegram.ext import Filters
import json
import csv
import re
from database import mydatabase
from handlers import *
import handlers


def main():

    # Create Tables
    # dbms.create_db_tables()

    # dbms.insert_single_data()
    # dbms.print_all_data(mydatabase.USERS)

    my_bot = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mydb.sqlite')
    hd = handlers.Handlers(dbms)
    my_bot.dispatcher.add_handler(CommandHandler('start', hd.sms))

    hd.hour_pars()
    expression = r'(https://[a-z]{1,3}.avito.ru/.*)'

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex("Установить наблюдение"), hd.start_observation)
                                          ],
                            allow_reentry=True,
                            states={
                                "link": [MessageHandler(Filters.regex(expression), hd.pars),
                                         MessageHandler(Filters.regex(
                                             "Отмена"), hd.answer_no),
                                         MessageHandler(Filters.text, hd.not_link)],
                                "confirm": [MessageHandler(Filters.regex("Да"), hd.answer_yes),
                                            MessageHandler(
                                                Filters.regex("Нет"), hd.answer_no)
                                            ]
        },
            fallbacks=[MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document, hd.try_again)]
        )
    )

    my_bot.dispatcher.add_handler(
        ConversationHandler(entry_points=[MessageHandler(Filters.regex("Мои подписки"), hd.subscription)],
                            allow_reentry=True,
                            states={
                                "delete_all": [MessageHandler(Filters.regex("Отписаться от всего"), hd.delete_all),
                                               MessageHandler(Filters.regex("Назад"), hd.cancel)]

        },
            fallbacks=[MessageHandler(
                Filters.text | Filters.video | Filters.photo | Filters.document, hd.try_again)]
        )
    )

    my_bot.dispatcher.add_handler(MessageHandler(
        Filters.text | Filters.video | Filters.photo | Filters.document, hd.donot_know))

    my_bot.dispatcher.add_handler(CallbackQueryHandler(hd.button_del, pattern=r'(Delete:)(\d+)'
                                                       ))  # Ловим коллбэк от кнопки. Нам передается объект CallbackQuery который содержит поле data и message. Сейчас нам нужно из даты достать наше слово которое мы передали в атрибуте callback_data

    my_bot.start_polling()  # Start the Bot
    my_bot.idle()      # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT


if __name__ == '__main__':
    main()
