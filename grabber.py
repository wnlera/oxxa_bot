from urllib.request import urlopen

import re
import requests
from bs4 import BeautifulSoup


def getShedUrl():
    try:
        url = 'https://www.mirea.ru/education/schedule-main/schedule/#tabs'
        page = urlopen(url)
        soup = BeautifulSoup(page.read(), "lxml")  # , from_encoding="utf-8")

        root = soup.find(True, attrs={"id": 'tab-content'})
        children = root.find_all(True, class_="uk-active", attrs={"aria-hidden": False})[0]

        paras = children.find_all(True, class_="uk-accordion-content")
        insts = children.find_all(True, class_="uk-accordion-title")
        # print(insts[2])
        xls = paras[2].find_all(True, class_="xls")[0].attrs['href']
        return xls
    except:
        print("MEOW")


def getWeekNum():
    url = 'https://www.mirea.ru/'

    page = urlopen(url)
    soup = BeautifulSoup(page.read(), "lxml")  # , from_encoding="utf-8")

    block = str(soup.find(True, class_="first_page_week"))
    r = re.compile("\d+-")

    return int(re.search(r, block).group(0)[0:-1])


def getWeather():
    summary = ''
    url = "http://api.wunderground.com/api/0c25613f6371174e/forecast/q/Russia/Moscow.json"
    response = requests.get(url)
    parsed_data = response.json()['forecast']['simpleforecast']['forecastday']

    ic = 0
    for day in parsed_data[1:2]:
        # date = "%s.%s.%s (%s)"%(day['date']['day'],day['date']['month'],day['date']['year'],day['date']['weekday'])
        temperature = day['high']['celsius']  # Температура днем
        cond = day['conditions']  # Условия
        wind = day['avewind']['mph']  # Ветер м/c
        PoP = day['pop']  # Шанс осадков в этот день
        # humidity = day['avehumidity'] # Влажность
        # qpf = max(day['qpf_allday']['mm'], day['snow_allday']['mm']) # Осдаки мм (max из снега и дождя)

        summary = ('%s\n'
                   'Температура днем: %s°С\n'
                   'Ветер: %s м/с\n'
                   'Вероятность осадков: %s%%') % (cond, temperature, wind, PoP)
    return summary


def getLastModifiedS(url):
    r = requests.head(url)
    lastm = r.headers['Last-Modified']
    print("new lastm: %s" % lastm)
    return lastm