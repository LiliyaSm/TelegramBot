from bs4 import BeautifulSoup
import requests
from utils import my_keyboard
from telegram import ReplyKeyboardMarkup
from database import mydatabase


class Handlers:

    def __init__(self, dbms):
        self.dbms = dbms
        self.dbms.create_db_tables()

    def sms(self, bot, update):
        print("'/start' was sent!")
        # добавляем кнопки
        bot.message.reply_text("Приветствую, {}. Нажимай на нужную кнопку"
                               .format(bot.message.chat.first_name),
                               reply_markup=my_keyboard())

        # pprint.pprint(bot.message)
        print(bot.message)
        # print(json.dumps(bot.message, indent=2))

    def get_html(self, url):
        r = requests.get(url)
        return r.text

    def check_price(self, html):
        soup = BeautifulSoup(html, 'lxml')
        try:
            price = soup.find('span', class_='js-item-price').text
            return price
        except Exception as e:
            print(e)
            return False

    def pars(self, bot, update):
        html = self.get_html(bot.message.text)
        print("avito link was sent!")
        price = self.check_price(html)
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

    def answer_yes(self, bot, update):
        try:
            user_id = bot.effective_user.id
            if self.dbms.data_insert(user_id, update.user_data["link"], update.user_data["price"]):

                bot.message.reply_text("Наблюдение установлено!",
                                       reply_markup=my_keyboard())
                return -1

            else:
                bot.message.reply_text("уже три ссылки под наблюдением, удалите ненужные",
                                       reply_markup=my_keyboard())

                return -1

        except Exception as ex:
            print(ex)
        return -1

    def answer_no(self, bot, update):
        bot.message.reply_text("Наблюдение не установлено!",
                               reply_markup=my_keyboard())
        return ConversationHandler.END

    def not_link(self, bot, update):
        print(bot.message.text)
        bot.message.reply_text("это не ссылка!")

    def donot_know(self, bot, update):
        bot.message.reply_text("не понимаю!(не разговор)",
                            reply_markup=my_keyboard())

    def try_again(self, bot, update):
        bot.message.reply_text("я не знаю такой команды! (разговор)",
                            )

    def start_observation(self, bot, update):
        reply_keyboard = [['Отмена']]
        bot.message.reply_text("пришлите ссылку на товар",
                               reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                one_time_keyboard=True,
                                                                resize_keyboard=True))

        return "link"

    def subscription(self, bot, update):
        try:
            user_id = bot.effective_user.id
            list_of_links = self.dbms.search(user_id)
            if len(list_of_links) > 0:
                for link in list_of_links:
                    bot.message.reply_text("{}".format(link),
                                           reply_markup=my_keyboard())

            else:
                bot.message.reply_text("У вас нет подписок")

        except Exception as ex:
            print(ex)
        return ConversationHandler.END
        bot.message.reply_text("У вас нет подписок")
