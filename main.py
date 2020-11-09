# -*- coding: utf-8 -*-
import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup
import time
from random import random

bot = telebot.TeleBot("1414986890:AAH5yUrdfwPhovZem0W2UDPhRGAzqPTFl3Q")
action = 0
discount = 20
server = 3061
items = [90045, 730, 729, 93256, 93255, 93629, 93628]

@bot.message_handler(func=lambda m: True)
def messages(message):
    global id_telegram
    global action
    global markup
    id_telegram = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn1 = types.KeyboardButton("/start")
    btn2 = types.KeyboardButton("/stop")
    markup.add(btn1, btn2)
    if action == 0:
        if message.text == "/start":
            action = 1
            bot.send_message(id_telegram, "мониторинг цен начался", parse_mode="html", reply_markup=markup)
    if action == 1:
        if message.text == "/stop":
            action = 2
        else:
            autocheck(items, server, discount)
def check_price(id, server, discount):
    if action == 2:
        return
    else:
        discount = discount/100
        link_to_parse = f'http://l2on.net/?c=market&a=item&id={id}&setworld={server}'
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15'}
        full_page = requests.get(link_to_parse, headers)

        # находит название товара
        soup = BeautifulSoup(full_page.text, 'html.parser')
        convert_name = soup.find_all("title")
        item_name = convert_name[0].text.replace(' / Рынок / L2on (база знаний L2)', '')

        # находит минимальную стоимость товара
        table = soup.findChildren('tbody')
        fresh = table[0].findChildren('tr',{'class': 'fresh'})
        min_price = float('inf')
        for raw in fresh:
            cells = raw.findChildren('td', {'class': "right"})
            if int(cells[0].text.replace(' ', '')) < min_price:
                min_price = int(cells[0].text.replace(' ', ''))

        # находит среднюю стоимость товара
        total_price = 0
        quantity = 0
        shop = table[0].findChildren('tr')
        for raw in shop:
            cells = raw.findChildren('td', {'class': "right"})
            total_price += int(cells[0].text.replace(' ', ''))*int(cells[1].text.replace(' ', ''))
            quantity += int(cells[1].text.replace(' ', ''))
        if quantity > 0:
            average_price = total_price / quantity

            # если минимальная цена ниже средней на х%, то возвращает сообщение, которое надо отправить в телеграмм
            if min_price/(1-discount)*1<average_price:
                send_mess = str(item_name)+" минимальная цена: "+str(min_price)+" средняя цена: "+str(average_price)
                bot.send_message(id_telegram, send_mess, parse_mode="html", reply_markup=markup)
        print(str(item_name)+" "+str(min_price))

def autocheck(items, server, discount):
    print("цикл")
    global action
    if action == 2:
        return
    else:
        time_multi = 10/len(items)
        if time_multi < 5:
            time_multi = 5
        for item in items:
            check_price(item, server, discount)
            random_sleep = int(random()*time_multi)
            time.sleep(random_sleep)
        if action == 2:
            bot.send_message(id_telegram, "мониторинг цен приостановлен", parse_mode="html", reply_markup=markup)
            action = 0
        if action == 1:
            autocheck(items, server, discount)
bot.polling(none_stop="True")
