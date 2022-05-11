import asyncio
import datetime
import pandas as pd
from typing import List

from Controller import *
from dcs import UpdateObj


class Logic:
    def __init__(self, UI_queue: asyncio.Queue, queue: asyncio.Queue, concurrent_workers: int):
        self.queue = queue
        self.__UI_queue = UI_queue
        self.__users = pd.read_csv('Users.csv', usecols=['user_id', 'token'])
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    # async def print(self, chat_id: int, txt: str):
    #     await self.__tg_user.send_message(chat_id, txt)

    async def registration(self, chat_id: int):
        if await self.find_id(chat_id):
            self.__UI_queue.put_nowait([chat_id, "Ты уже зарегистрирован!"])
        #   await Controller.print_ui(chat_id, "Ты уже зарегистрирован!")
        #   await self.__tg_user.send_message(chat_id, "Ты уже зарегистрирован!")
            return
        self.__UI_queue.put_nowait([chat_id, "Введи свой инвестиционный токен"])
        upd = await self.queue.get()
        while True:
            token = upd.message.text
            await self.add_token(chat_id, token)
            self.__UI_queue.put_nowait([chat_id, "Записал😉"])
            return

    async def distribution(self, upd: UpdateObj):
        mes = upd.message.text
        chat_id = upd.message.chat.id
        if mes == '/start':
            await self.registration(chat_id)
        elif mes != "":
            if not await self.find_id(chat_id):
                self.__UI_queue.put_nowait([chat_id, "Ты не зарегистрирован!\n"
                                                         "Чтобы получить доступ к полному функционалу напиши /start и зарегистрируйся"])

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

    async def find_id(self, user_id: int):
        return any(self.__users.user_id == user_id)
