from bs4 import BeautifulSoup
import requests
from utils import my_keyboard, cancel_keyboard
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from database import mydatabase
import re


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

    def get_price(self, url):
        r = requests.get(url)
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        not_actual = soup.find('div', class_='item-view-warning-content')
        if not not_actual:  # если объявление актуально
            try:
                price = soup.find('span', class_='js-item-price').text
                try:
                    price = int(price.replace(" ", ""))
                    return price
                except ValueError:
                    print("can't price turn into int")
            except AttributeError:
                try:
                    price = soup.find('span', class_='price-value-string').text
                    return price.strip()   # Если цена Бесплатнo или не указана
                except Exception as e:
                    print(e)
                    return None
        else:
            return "Архив"

    def mobile_link(self, link):
        if re.search(r'https://m.avito.ru/.*', link):
            link = re.sub(r'm', "www", link, 1)
        return link

    def pars(self, bot, update):
        link = self.mobile_link(bot.message.text)
        price = self.get_price(link)

        print("avito link was sent!")

        if price == "Архив":
            bot.message.reply_text("Это объявление неактульно. Попробуйте другой товар",
                                   reply_markup=cancel_keyboard())
            return "link"

        elif price:
            update.user_data["link"] = bot.message.text
            print(price)
            update.user_data["price"] = price
            bot.message.reply_text("Цена товара: {}".format(price))

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

    def hour_pars(self):
        dict_to_pars = self.dbms.time_check()
        if dict_to_pars:
            for i in range(len(dict_to_pars)):
                new_price = self.get_price(
                    dict_to_pars[i][1])  # id, link, price
                if new_price == "Архив":
                    self.dbms.update_price(dict_to_pars[i][0], new_price)
                    pass
                elif new_price == None:
                    pass
                elif new_price != dict_to_pars[i][2]:
                    # сделать через один запрос
                    self.dbms.update_price(dict_to_pars[i][0], new_price)

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
        bot.message.reply_text("Выберите команду",
                               reply_markup=my_keyboard())
        return -1

    def not_link(self, bot, update):
        print(bot.message.text)
        bot.message.reply_text("это не ссылка!")

    def donot_know(self, bot, update):
        bot.message.reply_text("Выберите сначала команду!",
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

                bot.message.reply_text("Для отписки от *ВСЕХ* рассылок нажмите кнопку",
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
        link_id = context.match[2]  # query.message.text
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
