import asyncio
import datetime
import pandas as pd
from typing import List
from User import *
from Controller import *
from dcs import UpdateObj


class Logic:
    def __init__(self, UI_queue: asyncio.Queue, queue: asyncio.Queue, concurrent_workers: int):
        self.queue = queue
        self.__UI_queue = UI_queue
        self.__users = pd.read_csv('Users.csv', usecols=['user_id', 'token'])
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []

    def print_ui(self, chat_id: int, mes: str):
        """
        Добавляет в очередь сообщения, которые нужно вывести
        """
        self.__UI_queue.put_nowait([chat_id, mes])

    async def registration(self, chat_id: int):
        """
        Регистрация пользователя в боте. Просим у пользователя его токен
        в Инвестициях и записываем его в pandas data frame Users.csv.
        Таким образом сопоставляем chat_id и токен в Инвестициях.
        """
        if await self.find_id(chat_id):
            self.print_ui(chat_id, "Ты уже зарегистрирован!")
            return
        self.print_ui(chat_id, "Введи свой инвестиционный токен")
        upd = await self.queue.get()
        while True:
            token = upd.message.text
            await self.add_token(chat_id, token)
            self.print_ui(chat_id, "Записал😉")
            return

    async def get_portfolio(self, chat_id: int):
        """
        Показываем пользователю его инвестиционное портфолио по токену,
        найденному в Users.csv по chat_id
        """
        try:
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            with Client(token) as client:
                us = User(token, client)
                portfolio = us.get_portfolio(account_id=us.get_account_id()).to_string()
                self.print_ui(chat_id, portfolio)

        except:
            self.print_ui(chat_id, "Токен оказался недействительным")

    async def buy_paper(self, chat_id: int):
        """
        Покупаем инвестиционную бумагу по figi пользователю с токеном,
        найденном в Users.csv по chat_id
        """
        self.print_ui(chat_id, "Укажи figi бумаги, которую хочешь купить\n"
                               "Figi - уникальный номер каждой бумаги, его можно узнать в интернете")
        upd = await self.queue.get()
        figi = upd.message.text
        self.print_ui(chat_id, f"Укажи количество бумаг с figi: {figi}, которое ты хочешь купить")
        upd = await self.queue.get()
        amount = upd.message.text
        users_to_loc = self.__users.set_index(['user_id'])
        token = users_to_loc.loc[chat_id].token
        try:
            with Client(token) as client:
                us = User(token, client)
                us.buy(account_id=us.get_account_id(), figi=figi, amount=int(amount))
                print('okgsks')
                self.print_ui(chat_id, "Бумага успешно куплена, можешь проверять порфтолио")
        except:
            self.print_ui(chat_id, "Figi оказался недействительным")


    async def sell(self, chat_id: int):
        """
        Покупаем инвестиционную бумагу по figi пользователю с токеном,
        найденном в Users.csv по chat_id
        """
        self.print_ui(chat_id, "Укажи figi бумаги, которую хочешь продать\n")
        upd = await self.queue.get()
        figi = upd.message.text
        self.print_ui(chat_id, f"Укажи количество лотов с figi: {figi}, которое ты хочешь продать")
        upd = await self.queue.get()
        amount = upd.message.text
        users_to_loc = self.__users.set_index(['user_id'])
        token = users_to_loc.loc[chat_id].token
        try:
            # Функция Богдана с учетом проверки корректности figi
            self.print_ui(chat_id, "Лоты успешно проданы, можешь проверять портфолио")
        except:
            self.print_ui(chat_id, "Figi оказался недействительным")


    async def plot(self, chat_id: int):
        """
        Выводим график бумаги по figi пользователю с токеном,
        найденном в Users.csv по chat_id
        """
        self.print_ui(chat_id, "Укажи figi бумаги, график которой ты хочешь видеть")
        upd = await self.queue.get()
        figi = upd.message.text
        users_to_loc = self.__users.set_index(['user_id'])
        token = users_to_loc.loc[chat_id].token
        try:
            pass
            #Функция Богдана с учетом проверки корректности figi
        except:
            self.print_ui(chat_id, "Figi оказался недействительным")


    async def distribution(self, upd: UpdateObj):
        """
         Вызывает функции в зависимости от поступившей команды
        """
        mes = upd.message.text
        chat_id = upd.message.chat.id
        if mes == '/start':
            await self.registration(chat_id)
        elif mes != "" and not await self.find_id(chat_id):
            self.print_ui(chat_id, "Ты не зарегистрирован!\n"
                                   "Чтобы получить доступ к полному функционалу напиши /start и зарегистрируйся")
        elif mes == "/portfolio":
            await self.get_portfolio(chat_id)
        elif mes == "/buy":
            await self.buy_paper(chat_id)
        elif mes == "/plot":
            await self.plot(chat_id)
        elif mes == "/sell":
            await self.sell(chat_id)
        else:
            self.print_ui(chat_id, "Попробуй воспользоваться функциями из меню")

    async def _worker(self):
        """
        Рабочий цикл, проверяющий обновление в очереди пришедших сообщений
        """
        while True:
            upd = await self.queue.get()
            #print(upd)
            try:
                await self.distribution(upd)
            finally:
                self.queue.task_done()

    async def start(self):
        """
        Ассинхронный запуск цикла worker
        """
        self._tasks = [asyncio.create_task(self._worker()) for _ in range(self.concurrent_workers)]

    async def stop(self):
        """
        Выключение ассинхронных задач
        """
        await self.queue.join()
        for t in self._tasks:
            t.cancel()

    async def add_token(self, user_id: int, token=0):
        """
        Дабавление токена по id пользователя из мессенджера
        """
        self.__users = self.__users.append({'user_id': user_id, 'token': token}, ignore_index=True)
        print(self.__users)
        # self.__users.to_csv('Users.csv')

    async def find_id(self, user_id: int):
        """
        Проверка присутствия пользователя с данным user_id в pd data frame Users.csv
        """
        return any(self.__users.user_id == user_id)
