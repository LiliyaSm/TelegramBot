from bs4 import BeautifulSoup
import requests
import re

def get_price(url):
    if re.search(r'https://www.avito.ru/.*', url):
        url = re.sub(r'www', "m", url, 1)
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    not_actual = soup.find('div', class_='item-view-warning-content')

    if not not_actual:  # если объявление актуально
        try:
            price = soup.find(
                'meta', {"itemprop": 'price'})["content"]
            if price.strip() == "Бесплатно":
                return (None, 1, 0)  # state = 1, archive = 0
            elif price.strip() == "Цена не указана":
                return (None, 2, 0)
            else:
                price = int(price.replace(" ", ""))
                return (price, 0, 0)
        except Exception as e:
            print(e)
            return (None, None, 1) # возможно удалено
    else:
        return (None, None, 1)  # archive = 1
