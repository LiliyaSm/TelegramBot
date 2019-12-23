from utils import my_keyboard, cancel_keyboard
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from parsing import get_price
import logging

module_logger = logging.getLogger("botLogger.handlers")

class Handlers:

    def __init__(self, dbms):
        self.dbms = dbms

    def sms(self, bot, update):
        logger = logging.getLogger("botLogger.handlers.sms")
        logger.info("/start was received")
        # добавляем кнопки
        bot.message.reply_text("Приветствую, {}. Нажимай на нужную кнопку"
                               .format(bot.message.chat.first_name),
                               reply_markup=my_keyboard())

        # pprint.pprint(bot.message)
        print(bot.message)
        # print(json.dumps(bot.message, indent=2))

    def pars(self, bot, update):
        price, state, archive = get_price(bot.message.text)

        print("avito link was sent!")

        if  archive:
            bot.message.reply_text("Это объявление неактульно. Попробуйте другой товар",
                                   reply_markup=cancel_keyboard())
            return "link"

        if state or price:
            if state == 0:
                bot.message.reply_text("Цена товара: {}".format(price))
            if state == 1:
                bot.message.reply_text("Товар отдается бесплатно")
            if state == 2:
                bot.message.reply_text("Цена товара не указана")
            
            update.user_data["link"] = bot.message.text
            update.user_data['state'] = state
            update.user_data["price"] = price
            reply_keyboard = [['Да', 'Нет']]
            bot.message.reply_text("Установить наблюдение?",
                                   reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                    one_time_keyboard=True,
                                                                    resize_keyboard=True))
            return "confirm"        
        bot.message.reply_text("Цена на странице не найдена :( Попробуйте ещё",
                                   reply_markup=cancel_keyboard())
        return "link"

    def answer_yes(self, bot, update):
        try:
            price = update.user_data["price"]
            state = update.user_data["state"]
            link = update.user_data["link"]
            tlg_id = bot.effective_user.id
            if self.dbms.data_insert(
                tlg_id, link, price, state):
                bot.message.reply_text("Наблюдение установлено! При изменении цены вам придёт уведомление",
                                    reply_markup=my_keyboard())
                return -1
            else:
                bot.message.reply_text("Наблюдение не установлено! Возможно, вы уже наблюдаете за этой ссылкой. Если вы уверены, что всё правильно, то попробуйте позже ещё раз",
                                        reply_markup=cancel_keyboard())
                return "link"
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
        tlg_id = bot.effective_user.id
        count = self.dbms.search_count(tlg_id)
        if count < 3:
            bot.message.reply_text("пришлите ссылку на товар",
                                   reply_markup=cancel_keyboard())
            return "link"
        else:
            bot.message.reply_text("уже три ссылки под наблюдением, удалите ненужные",
                                   reply_markup=my_keyboard())
            return -1

    def delete_all(self, bot, update):
        tlg_id = bot.effective_user.id
        self.dbms.delete_link(tlg_id)
        bot.message.reply_text("У вас больше нет подписок!",
                                   reply_markup=my_keyboard())
        return -1

    def subscription(self, bot, update):
        try:
            tlg_id = bot.effective_user.id
            list_of_links = self.dbms.search(tlg_id)
            if len(list_of_links) > 0:
                reply_keyboard = [['Назад', 'Отписаться от всего']]

                #update.user_data["number_links"] = len(list_of_links)

                for link in list_of_links:
                    keyboard = [[InlineKeyboardButton(
                        "Отписаться от рассылки по этому товару", callback_data='Delete:' + str(link.id))]]
                    reply_markup = InlineKeyboardMarkup(keyboard)

                    bot.message.reply_text("{}".format(link.link),
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
        tlg_id = update.effective_user.id
        query = update.callback_query
        link_id = context.match[2]  # query.message.text
        print(link_id)
        if self.dbms.delete_link(tlg_id, link_id):
            keyboard = [[InlineKeyboardButton(
                "Удалено", callback_data='Done')]]
            context.bot.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(keyboard),
                chat_id=query.message.chat.id,
                message_id=query.message.message_id,
            )
        else:
            pass


def send_alarm(bot, notification):
    try:
        logger = logging.getLogger("botLogger.handlers.send_alarm")      

        if notification["archive"]:
            bot.send_message(notification["tlg_id"], "Объявление снято с публикации! Его отслеживание прекращено {0} "
                             .format(notification["link"]))
            logger.info("message was sent: ", notification["tlg_id"], "Объявление снято с публикации! Его отслеживание прекращено {0} "
                        .format(notification["link"]))
            return
        if notification["old"]:
            bot.send_message(notification["tlg_id"], "Закончился срок отслеживания объявления {0} "
                            .format(notification["link"]))
            logger.info("message was sent: ", notification["tlg_id"], "Закончился срок отслеживания объявления {0} "
                        .format(notification["link"]))
            return                            
        if not notification["price"]:
            notification["price"] = "не указана"
        elif not notification["new_price"]:
            notification["new_price"] = "не указана"
        #bot.sendMessage(chat_id=chat_id, text=msg)
        bot.send_message(notification["tlg_id"], "Цена на отслеживаемый товар изменилась! {0}, предыдущая цена: {1}. <b>Новая цена: {2} </b>"
                         .format(notification["link"], notification["price"], notification["new_price"]),
                        parse_mode="HTML")
        "Закончился срок отслеживания объявления {0} "
        logger.info("message was sent: " + str(notification["tlg_id"]) + "Цена на отслеживаемый товар изменилась! {0}, предыдущая цена: {1}. Новая цена: {2}"
            .format(notification["link"], notification["price"], notification["new_price"]))
    except Exception as ex:
        print(ex)
        logger.exception(ex)
        
