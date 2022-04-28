import requests
import asyncio
from Logic import *
import telebot
import pandas as pd

API_link = "https://api.telegram.org/bot5205698417:AAFeZkm72W8qdzbaYNc_TjDmE2UxEmtWvpw"

req = []


def wait():
    req_sz = len(req)
    id = req[0]['from']['id']
    while len(req) == req_sz or req[len(req) - 1]['from']['id'] != id:
        update()


offset = 0


def update():
    updates = requests.get(API_link + "/getUpdates?timeout=600&offset=offset").json()
    for item in updates["result"]:
        offset = item["update_id"] + 1
    if not updates['result'][-1]['message'] in req:
        req.append(updates['result'][-1]['message'])
    message = updates['result'][-1]['message']
    text = message['text']
    user_id = message['from']['id']
    chat_id = message['chat']['id']
    mes_id = message['message_id']
    return text, chat_id, user_id, mes_id


async def registration(logic, chat_id, user_id):
    if not logic.find_id(user_id):
        requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Введи свой инвестиционный токен")
        wait()
        token = update()[0]
        logic.add(user_id, token)
        requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Записал😉")
    else:
        requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Ты уже зарегистрирован")


async def start(logic1, last_mes=0):
    while True:
        update()
        if len(req) > 0:
            text = req[0]['text']
            chat_id = req[0]['chat']['id']
            user_id = req[0]['from']['id']
            mes_id = req[0]['message_id']

            if last_mes != mes_id:
                last_mes = mes_id
                if text == '/start':
                    await registration(logic1, chat_id, user_id)
                elif logic1.find_id(user_id):
                    requests.get(
                        API_link + f"/sendMessage?chat_id={chat_id}&text=Совсем скоро тут будут доступны функции для тебя")
                else:
                    requests.get(
                        API_link + f"/sendMessage?chat_id={chat_id}&text=Тебе нужно зарегистрироваться! Напиши /start")
            req.pop(0)


logic = Logic()
asyncio.run(start(logic))
# us1 = pd.DataFrame(columns=['user_id', 'token'])
# us1.to_csv('Users.csv')
# us = us.append({'user_id': user_id, 'token': 1234}, ignore_index=True)
# print(us)

# send_message = requests.get(API_link + f"/sendMessage?chat_id={chat_id}&text=Добро пожаловать на платформу для инвестирования!")
