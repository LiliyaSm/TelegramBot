from bs4 import BeautifulSoup
import requests
from utils import my_keyboard
from telegram import ReplyKeyboardMarkup
from database import mydatabase

def sms(bot, update):
    print("'/start' was sent!")
    # добавляем кнопки
    bot.message.reply_text("Приветствую, {}. Нажимай на нужную кнопку"
                           .format(bot.message.chat.first_name),
                           reply_markup=my_keyboard())

    # pprint.pprint(bot.message)
    print(bot.message)
    # print(json.dumps(bot.message, indent=2))


def get_html(url):
    r = requests.get(url)
    return r.text


def check_price(html):
    soup = BeautifulSoup(html, 'lxml')
    try:
        price = soup.find('span', class_='js-item-price').text
        return price
    except Exception as e:
        print(e)
        return False


def pars(bot, update):
    html = get_html(bot.message.text)
    print("avito link was sent!")
    price = check_price(html)
    if price:
        update.user_data["link"] = bot.message.text
        print(price)
        update.user_data["price"] = price
        bot.message.reply_text("Цена товара: " + price)

        reply_keyboard = [['Да', 'Нет']]
        bot.message.reply_text("Установить наблюдение?",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                one_time_keyboard=True,
                                                                resize_keyboard=True))
        return "confirm"
    else:
        reply_keyboard = [['Отмена']]
        bot.message.reply_text("цена на странице не найдена :( Попробуйте ещё",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                one_time_keyboard=True,
                                                                resize_keyboard=True))
        return "link"


def answer_yes(bot, update):
    try:
        dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mydb.sqlite')
        user_id = bot.effective_user.id
        if dbms.data_insert(user_id, update.user_data["link"], update.user_data["price"]):

            bot.message.reply_text("Наблюдение установлено!",
                                reply_markup=my_keyboard())
            return ConversationHandler.END
            
        else:
            bot.message.reply_text("уже три ссылки под наблюдением, удалите ненужные",
                                reply_markup=my_keyboard())
            
            return ConversationHandler.END

    except Exception as ex:
        print(ex)
    return ConversationHandler.END


def answer_no(bot, update):
    bot.message.reply_text("Наблюдение не установлено!",
                           reply_markup=my_keyboard())
    return ConversationHandler.END


def not_link(bot, update):
    print(bot.message.text)
    bot.message.reply_text("это не ссылка!")


def donot_know(bot, update):
    bot.message.reply_text("я не знаю такой команды!")


def start_observation(bot, update):
    reply_keyboard = [['Отмена']]
    bot.message.reply_text("пришлите ссылку на товар",
                           reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                            one_time_keyboard=True,
                                                            resize_keyboard=True))

    return "link"


def subscription(bot, update):
    try:
        dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mydb.sqlite')
        dbms.create_db_tables()
        user_id = bot.effective_user.id
        if dbms.search(user_id):
            user_id = bot.effective_user.id
            bot.message.reply_text("{}".format(result),
                                reply_markup=my_keyboard())
            
        else:
            bot.message.reply_text("У вас нет подписок")

    except Exception as ex:
        print(ex)
    return ConversationHandler.END    
    bot.message.reply_text("У вас нет подписок")
