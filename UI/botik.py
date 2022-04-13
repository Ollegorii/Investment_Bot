import requests
from Logic import *
import pandas as pd

API_link = "https://api.telegram.org/bot5205698417:AAFeZkm72W8qdzbaYNc_TjDmE2UxEmtWvpw"


def wait(last_m, user_id):
    while last_m == update()[3] or update()[2] != user_id:
        pass


def update():
    updates = requests.get(API_link + "/getUpdates?offset=-1").json()
    message = updates['result'][0]['message']
    text = message['text']
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    mes_id = message['message_id']
    return text, chat_id, user_id, mes_id


def registration(logic, chat_id, user_id):
    if not logic.find_id(user_id):
        last_m = update()[3]
        requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Введи свой инвестиционный токен")
        wait(last_m, user_id)
        token = update()[0]
        logic.add(user_id, token)
        requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Записал😉")
    else:
        requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Ты уже зарегистрирован")


# us1 = pd.DataFrame(columns=['user_id', 'token'])
# us1.to_csv('Users.csv')
# us = us.append({'user_id': user_id, 'token': 1234}, ignore_index=True)
# print(us)

last_mes = 0
logic = Logic()

while True:
    text, chat_id, user_id, mes_id = update()
    if last_mes != mes_id:
        last_mes = mes_id
        if text == '/start':
            registration(logic, chat_id, user_id)
        elif logic.find_id(user_id):
            requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Совсем скоро тут будут доступны функции для тебя")
        else:
            requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Тебе нужно зарегистрироваться! Напиши /start")

# send_message = requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Добро пожаловать на платформу для инвестирования!")
