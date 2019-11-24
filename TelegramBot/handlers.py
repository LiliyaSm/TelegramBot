from bs4 import BeautifulSoup
import requests
from utils import my_keyboard


def sms(bot, update):
    print("'/start' was sent!")
    # добавляем кнопки
    bot.message.reply_text("Приветствую, {}. Нажимай на нужную кнопку".format(bot.message.chat.first_name),
                           reply_markup=my_keyboard())

    # pprint.pprint(bot.message)
    print(bot.message)
    # print(json.dumps(bot.message, indent=2))


def get_html(url):
    r = requests.get(url)
    return r.text


def pars(bot, update):
    print("link was sent!")
    html = get_html(bot.message.text)    # сообщение из чата
    soup = BeautifulSoup(html, 'lxml')

    try:
        price = soup.find('span', class_='js-item-price').text
    except:
        bot.message.reply_text("цена на странице не найдена :(")

    print(price)
    bot.message.reply_text("Цена товара: " + price)
    return price


def parrot(bot, update):
    print(bot.message.text)
    bot.message.reply_text("это не ссылка!")
