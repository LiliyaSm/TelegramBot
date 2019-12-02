from bs4 import BeautifulSoup
import requests
from utils import my_keyboard, cancel_keyboard
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
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
            bot.message.reply_text("Цена на странице не найдена :( Попробуйте ещё",
                                   reply_markup=cancel_keyboard())
            return "link"

    def answer_yes(self, bot, update):
        try:
            user_id = bot.effective_user.id
            self.dbms.data_insert(
                user_id, update.user_data["link"], update.user_data["price"])

            bot.message.reply_text("Наблюдение установлено! При изменении цены вам придёт уведомление",
                                   reply_markup=my_keyboard())
            return -1

        except Exception as ex:
            print(ex)
        return -1

    def answer_no(self, bot, update):
        bot.message.reply_text("Наблюдение не установлено!",
                               reply_markup=my_keyboard())
        return -1

    def cancel(self, bot, update):
        bot.message.reply_text("Выберете команду",
                               reply_markup=my_keyboard())
        return -1

    def not_link(self, bot, update):
        print(bot.message.text)
        bot.message.reply_text("это не ссылка!")

    def donot_know(self, bot, update):
        bot.message.reply_text("Я вас не понимаю! Нажмите на нужную кнопку",
                               reply_markup=my_keyboard())

    def try_again(self, bot, update):
        bot.message.reply_text("Я не знаю такой команды!",
                               )

    def start_observation(self, bot, update):
        user_id = bot.effective_user.id
        if self.dbms.search_count(user_id) < 3:
            bot.message.reply_text("пришлите ссылку на товар",
                                   reply_markup=cancel_keyboard())

            return "link"
        else:
            bot.message.reply_text("уже три ссылки под наблюдением, удалите ненужные",
                                   reply_markup=my_keyboard())

            return -1


    def delete_all(self, bot, update):
        user_id = bot.effective_user.id
        if self.dbms.delete_link(user_id):

            bot.message.reply_text("У вас больше нет подписок!",
                               reply_markup=my_keyboard())

        else:
            pass
        return -1

    # def delete_link(self, bot, update):
    #     reply_keyboard = [['Да', 'Нет']]
    #     user_id = bot.effective_user.id
    #     update.user_data["link_id"] = bot.message.text
    #     if self.dbms.find_number(user_id, update.user_data["link_id"]):
    #         bot.message.reply_text("Объявление удалено")
    #         update.user_data["number_links"] = update.user_data["number_links"] - 1
    #         if update.user_data["number_links"] > 0:

    #             bot.message.reply_text("Продолжить удаление подписок?",
    #                                    reply_markup=ReplyKeyboardMarkup(reply_keyboard,
    #                                                                     one_time_keyboard=True,
    #                                                                     resize_keyboard=True))
    #             return "ask_again_link_number"
    #         else:
    #             bot.message.reply_text("У вас больше нет подписок!",
    #                                    reply_markup=my_keyboard())
    #             return -1
    #     else:
    #         bot.message.reply_text("Объявление не найдено",
    #                                reply_markup=my_keyboard())
    #         bot.message.reply_text("Продолжить удаление подписок?",
    #                                reply_markup=ReplyKeyboardMarkup(reply_keyboard,
    #                                                                 one_time_keyboard=True,
    #                                                                 resize_keyboard=True))
    #         return "ask_again_link_number"
    #     return -1

    def subscription(self, bot, update):
        try:
            user_id = bot.effective_user.id
            list_of_links = self.dbms.search(user_id)
            if len(list_of_links) > 0:
                reply_keyboard = [['Назад', 'Отписаться от всего']]

                #update.user_data["number_links"] = len(list_of_links)

                for key, link in list_of_links.items():
                    keyboard = [[InlineKeyboardButton(
                    "Отписаться от рассылки по этому товару", callback_data='Delete:' + str(key))]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                    bot.message.reply_text("{}".format(link),
                                           reply_markup=reply_markup)
                
                bot.message.reply_text("Для отписки от *всех* рассылок нажмите кнопку",
                                        parse_mode=ParseMode.MARKDOWN,
                                       reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                        one_time_keyboard=True,
                                                                        resize_keyboard=True,
                                                                       ))
                return "delete_all"
            else:
                bot.message.reply_text("У вас нет подписок",
                                       reply_markup=my_keyboard())
                return -1

        except Exception as ex:
            print(ex)
        

    def button_del(self, update, context):
        print(context.match)
        user_id = update.effective_user.id
        query = update.callback_query
        link_id = context.match[2]                                                   #query.message.text
        print(link_id)
        if self.dbms.delete_link(user_id, link_id):
            keyboard = [[InlineKeyboardButton(
                "Удалено", callback_data='Done')]]
            context.bot.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(keyboard),
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
            )            
        else:
            pass
