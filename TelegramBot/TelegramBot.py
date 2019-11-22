from telegram.ext import Updater

TOKEN = None

with open("key.txt") as f:
    TOKEN = f.read().strip()

def main():
    my_bot = Updater("TOKEN", "https://telegg.ru/otig/bot", use_context=True)
    my_bot.start_polling()
    my_bot.idle()

main()