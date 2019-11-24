from telegram import ReplyKeyboardMarkup


def my_keyboard():
    my_keyboard = ReplyKeyboardMarkup(
        [["/start"], ["Установить наблюдение"]],  resize_keyboard=True)
    return my_keyboard
