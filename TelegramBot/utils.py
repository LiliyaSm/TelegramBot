from telegram import ReplyKeyboardMarkup


def my_keyboard():
    my_keyboard = ReplyKeyboardMarkup(
        [["Установить наблюдение", "Мои подписки"]], 
         resize_keyboard=True)
    return my_keyboard
