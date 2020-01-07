import csv
import json
import re
import threading
from telegram import InlineKeyboardButton  # python-telegram-bot
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler,
                          Updater)

import handlers
import mydatabase  
from handlers import Handlers, send_alarm
from settings import TG_API_URL, TG_TOKEN
import telegram
import logging
import logging.config

def main():
    # Create Tables
    # dbms.create_db_tables()

    # dbms.insert_single_data()
    # dbms.print_all_data(mydatabase.USERS)

    logger.info("Program started")

    updater = Updater(TG_TOKEN, TG_API_URL, use_context=True)
    dbms = mydatabase.MyDatabase()
    hd = handlers.Handlers(dbms)
    updater.dispatcher.add_handler(CommandHandler('start', hd.sms))

    bot = telegram.Bot(token=TG_TOKEN, base_url=TG_API_URL)
    
    dbms.hour_pars(lambda notification: send_alarm(
        bot, notification))

    dbms.del_old(lambda notification: send_alarm(
      bot, notification))

    expression = r'^(?i).*(https://[a-z]{1,3}.avito.ru/.*)'
    

    updater.dispatcher.add_handler(
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

    updater.dispatcher.add_handler(
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

    updater.dispatcher.add_handler(MessageHandler(
        Filters.text | Filters.video | Filters.photo | Filters.document, hd.donot_know))

    updater.dispatcher.add_handler(CallbackQueryHandler(hd.button_del, pattern=r'(Delete:)(\d+)'

                                                       ))  # Ловим коллбэк от кнопки. Нам передается объект CallbackQuery который содержит поле data и message. Сейчас нам нужно из даты достать наше слово которое мы передали в атрибуте callback_data

    updater.start_polling()  # Start the Bot
    updater.idle()      # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT


if __name__ == '__main__':
    logging.config.fileConfig(
        fname='../file.conf', disable_existing_loggers=False)
    logger = logging.getLogger("botLogger")
    main()
