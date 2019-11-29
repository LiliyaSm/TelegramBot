from telegram import ReplyKeyboardMarkup


def my_keyboard():
    my_keyboard = ReplyKeyboardMarkup(
        [["Установить наблюдение", "Мои подписки"]], 
         resize_keyboard=True)
    return my_keyboard


def cancel_keyboard():
    cancel_keyboard = ReplyKeyboardMarkup( 
        [['Отмена']],
        one_time_keyboard=True,
        resize_keyboard=True)
    return cancel_keyboard
