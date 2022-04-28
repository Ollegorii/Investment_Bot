import asyncio
import datetime
import pandas as pd
from typing import List

from TgClient import *
from dcs import UpdateObj


class Worker:
    def __init__(self, token: str, queue: asyncio.Queue, concurrent_workers: int):
        self.tg_client = TgClient(token)
        self.queue = queue
        self.__users = pd.read_csv('Users.csv', usecols=['user_id', 'token'])
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    async def registration(self, chat_id: str):
        if await self.find_id(chat_id):
            await self.tg_client.send_message(chat_id, "Ты уже зарегистрирован!")
            return
        await self.tg_client.send_message(chat_id, "Введи свой инвестиционный токен")
        upd = await self.queue.get()
        while True:
            token = upd.message.text
            await self.add_token(chat_id, token)
            await self.tg_client.send_message(chat_id, "Записал😉")
            return

    async def distribution(self, upd: UpdateObj):
        mes = upd.message.text
        chat_id = upd.message.chat.id
        if mes == '/start':
            await self.registration(chat_id)
        elif mes != "":
            if not await self.find_id(chat_id):
                await self.tg_client.send_message(chat_id, "Ты не зарегистрирован!\n"
                "Чтобы получить доступ к полному функционалу напиши /start и зарегистрируйся")

    async def _worker(self):
        while True:
            upd = await self.queue.get()
            chat_id = upd.message.chat.id
            print(upd)
            try:
                await self.distribution(upd)
            finally:
                self.queue.task_done()

    async def start(self):
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.concurrent_workers)]

    async def stop(self):
        await self.queue.join()
        for t in self._tasks:
            t.cancel()

    async def add_token(self, user_id, token=0):
        self.__users = self.__users.append({'user_id': user_id, 'token': token}, ignore_index=True)
        print(self.__users)
        # self.__users.to_csv('Users.csv')

    async def find_id(self, user_id):
        return any(self.__users.user_id == user_id)
