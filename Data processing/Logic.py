import asyncio
import datetime
import pandas as pd
from typing import List
from User import *
from Controller import *
from dcs import UpdateObj
import GDrive


class Logic:
    def __init__(self, UI_queue: asyncio.Queue, queue: asyncio.Queue, concurrent_workers: int, GD: GDrive):
        self.queue = queue
        self.__UI_queue = UI_queue
        self.__users = pd.read_csv('Users.csv', usecols=['user_id', 'token'])
        self.concurrent_workers = concurrent_workers
        self._tasks: List[asyncio.Task] = []
        self.__GD = GD

    def print_ui(self, chat_id: int, mes: str, mes_id: int = 0):  # mes_id: 0 - text, 1 - photo
        self.__UI_queue.put_nowait([chat_id, mes, mes_id])

    async def registration(self, chat_id: int):
        """
        Регистрация пользователя в боте. Просим у пользователя его токен
        в Инвестициях и записываем его в pandas data frame Users.csv.
        Таким образом сопоставляем chat_id и токен в Инвестициях.
        """
        if await self.find_id(chat_id):
            self.print_ui(chat_id,
                          "Ты уже зарегистрирован!\nЕсли хочешь поменять токен, используй функцию /change_token")
            return
        self.print_ui(chat_id, "Введи свой инвестиционный токен")
        upd = await self.queue.get()
        # while True:
        token = upd.message.text
        await self.add_token(chat_id, token)
        self.print_ui(chat_id, "Записал😉")
        # return

    async def get_portfolio(self, chat_id: int):
        """
        Показываем пользователю его инвестиционное портфолио по токену,
        найденному в Users.csv по chat_id
        """
        try:
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            print(token)
            with Client(token) as client:
                us = User(token, client, self.__GD)
                portfolio = us.df_to_url(us.get_portfolio(account_id=us.get_account_id()))
                self.print_ui(chat_id, portfolio)
                self.print_ui(chat_id, portfolio, mes_id=1)  # mes_id: 0 - text, 1 - photo
        except FigiError:
            self.print_ui(chat_id, "Figi оказался недействительным")
        except:
            self.print_ui(chat_id, "Токен оказался недействительным"
                                   "\nЕсли хочешь поменять токен, используй функцию /change_token")

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
                us = User(token, client, self.__GD)
                us.buy(account_id=us.get_account_id(), figi=figi, amount=int(amount))
                self.print_ui(chat_id, "Бумага успешно куплена, можешь проверять порфтолио")
        except FigiError:
            self.print_ui(chat_id, "Figi оказался недействительным")
        except AmountError:
            self.print_ui(chat_id, "Количество оказалось недействительным")
        except:
            self.print_ui(chat_id, "Токен оказался недействительным"
                                   "\nЕсли хочешь поменять токен, используй функцию /change_token")

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
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            print(token)
            with Client(token) as client:
                us = User(token, client, self.__GD)
                url = us.get_candles(figi=figi, day_int=150)
                self.print_ui(chat_id, url)
                self.print_ui(chat_id, url, mes_id=1)  # mes_id: 0 - text, 1 - photo
        except:
            self.print_ui(chat_id, "Figi оказался недействительным")

    async def get_limits(self, chat_id: int):
        """
        Функция получает и выводит список лимитных заявок
        """
        try:
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            with Client(token) as client:
                us = User(token, client, self.__GD)
                df = us.get_orders(us.get_account_id())
                url = us.df_to_url(df)
                self.print_ui(chat_id, url)
                self.print_ui(chat_id, url, mes_id=1)  # mes_id: 0 - text, 1 - photo
        except EmptyData:
            self.print_ui(chat_id, "Список твоих заявок пуст")
        except:
            self.print_ui(chat_id, "Токен оказался недействительным"
                                   "\nЕсли хочешь поменять токен, используй функцию /change_token")

    async def buy_limit(self, chat_id: int):
        """
        Функция просит у пользователя figi, количество и стоимость бумаг,
        на которые необходимо выставить заявку на покупку. Затем выставляет заявку
        """
        self.print_ui(chat_id,
                      "Режим покупки лимитной зявки работает в боте лучше, чем в приложениях. Здесь нет срока на лимитные заявки"
                      " - она не удалится через сутки, но ты всегда можешь ее отменить командой /cancel_limits")
        self.print_ui(chat_id, "Введи figi бумаги, по которой хочешь выставить лимитную заявку")
        upd = await self.queue.get()
        figi = upd.message.text
        self.print_ui(chat_id, "Введи желаемое к покупке количество бумаг")
        upd = await self.queue.get()
        cnt = upd.message.text
        try:
            amount = int(cnt)
        except ValueError:
            self.print_ui(chat_id, "Ты ввел не число. Для еще одной попытке вызови /buy_limits повторно")
            return
        self.print_ui(chat_id, "Введи цену, по которой желаешь купить бумагу")
        upd = await self.queue.get()
        price = upd.message.text
        try:
            price = int(price)
        except ValueError:
            self.print_ui(chat_id, "Ты ввел не число. Для еще одной попытке вызови /buy_limits повторно")
            return
        try:
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            with Client(token) as client:
                us = User(token, client, self.__GD)
                us.buy_limit(account_id=us.get_account_id(), figi=figi, amount=int(amount), price=price)
                self.print_ui(chat_id, "Заявка успешно создана")
        except:
            self.print_ui(chat_id, "Figi оказался недействительным")

    async def sell_paper(self, chat_id: int):
        """
        Продаем инвестиционную бумагу по figi пользователю с токеном,
        найденном в Users.csv по chat_id
        """
        self.print_ui(chat_id, "Укажи figi бумаги, которую хочешь продать")
        upd = await self.queue.get()
        figi = upd.message.text
        self.print_ui(chat_id, f"Укажи количество бумаг с figi: {figi}, которое ты хочешь продать")
        upd = await self.queue.get()
        amount = upd.message.text
        try:
            amount = int(amount)
        except ValueError:
            self.print_ui(chat_id, "Ты ввел не число. Для еще одной попытке вызови /sell_limits повторно")
            return
        users_to_loc = self.__users.set_index(['user_id'])
        token = users_to_loc.loc[chat_id].token
        try:
            with Client(token) as client:
                us = User(token, client, self.__GD)
                us.sell(account_id=us.get_account_id(), figi=figi, amount=int(amount))
                self.print_ui(chat_id, "Бумага успешно продана")
        except FigiError:
            self.print_ui(chat_id, "Figi оказался недействительным")
        except AmountError:
            self.print_ui(chat_id, "Количество оказалось недействительным")
        except:
            self.print_ui(chat_id, "Токен оказался недействительным"
                                   "\nЕсли хочешь поменять токен, используй функцию /change_token")

    async def last_price(self, chat_id: int):
        """
        Функция получает с биржи последнюю цену бумаги
        с указанным figi и её выводит пользователю
        """
        self.print_ui(chat_id, "Укажи figi бумаги, цену которой хочешь узнать\n"
                               "Увидеть список бумаг и их figi можно с помощнью /get_figi")
        upd = await self.queue.get()
        figi = upd.message.text
        if figi == "/get_figi":
            await self.get_figi(chat_id)
            return
        users_to_loc = self.__users.set_index(['user_id'])
        token = users_to_loc.loc[chat_id].token
        try:
            with Client(token) as client:
                us = User(token, client, self.__GD)
                price = us.get_last_price(figi=figi)
                self.print_ui(chat_id, f"Стоимость бумаги: {price}")
        except FigiError:
            self.print_ui(chat_id, "Figi оказался недействительным")
        except:
            self.print_ui(chat_id, "Токен оказался недействительным"
                                   "\nЕсли хочешь поменять токен, используй функцию /change_token")

    async def sell_limit(self, chat_id: int):
        """
        Функция просит у пользователя figi, количество и стоимость бумаг,
        на которые необходимо выставить заявку на продажу. Затем выставляет заявку
        """
        self.print_ui(chat_id,
                      "Режим покупки лимитной зявки работает в боте лучше, чем в приложениях. Здесь нет срока на лимитные заявки"
                      " - она не удалится через сутки, но ты всегда можешь ее отменить командой /cancel_limits")
        self.print_ui(chat_id, "Введи figi бумаги, по которой хочешь выставить лимитную заявку")
        upd = await self.queue.get()
        figi = upd.message.text
        self.print_ui(chat_id, "Введи желаемое к продаже количество бумаг")
        upd = await self.queue.get()
        cnt = upd.message.text
        try:
            amount = int(cnt)
        except ValueError:
            self.print_ui(chat_id, "Ты ввел не число. Для еще одной попытке вызови /sell_limits повторно")
            return
        self.print_ui(chat_id, "Введи цену, по которой желаешь продать бумагу")
        upd = await self.queue.get()
        price = upd.message.text
        try:
            price = int(price)
        except ValueError:
            self.print_ui(chat_id, "Ты ввел не число. Для еще одной попытке вызови /sell_limits повторно")
            return
        try:
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            with Client(token) as client:
                us = User(token, client, self.__GD)
                us.sell_limit(account_id=us.get_account_id(), figi=figi, amount=int(amount), price=price)
                self.print_ui(chat_id, "Заявка успешно создана")
        except:
            self.print_ui(chat_id, "Figi оказался недействительным")

    async def cancel_limit(self, chat_id: int):
        """
        Отмена лимитной заявки по номеру из списка заявок
        """
        self.print_ui(chat_id, "Введи номер лимитной заявки, которую нужно отменить\n"
                               "Номер заявки можно посмтотреть в списке заявок командой /limits")
        upd = await self.queue.get()
        num = upd.message.text
        try:
            num = int(num)
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            with Client(token) as client:
                us = User(token, client, self.__GD)
                us.cancel_order_by_number(us.get_account_id(), num)
                self.print_ui(chat_id, "Заявка успешно отменена")
        except InputError:
            self.print_ui(chat_id, "Ты ввел некоректный номер заявки")
        except ValueError:
            self.print_ui(chat_id, "Ты ввел не число, нужен номер лимитной заявки")
        except:
            self.print_ui(chat_id, "Что-то пошло не так")

    async def get_figi(self, chat_id: int):
        """
        Посылает пользователю список всех бумаг и их figi,
        ведь в интеренете их найти порой сложно
        """
        try:
            users_to_loc = self.__users.set_index(['user_id'])
            token = users_to_loc.loc[chat_id].token
            with Client(token) as client:
                us = User(token, client, self.__GD)
                url = us.get_all_figies()
                self.print_ui(chat_id, "Сейчас пришлю тебе список всех бумаг и их figi. "
                                       "Воспользуйся поиском по файлу, чтобы найти нужную бумагу.")
                self.print_ui(chat_id, url)
        except:
            self.print_ui(chat_id, "Токен оказался недействительным"
                                   "\nЕсли хочешь поменять токен, используй функцию /change_token")




    async def change_token(self, chat_id: int):
        """
        Изменяет инвестиционный токен уже зарегистрированного
        пользователя (если вдруг ввел неверный)
        """
        self.print_ui(chat_id, "Введи новый инвестиционный токен")
        upd = await self.queue.get()
        token = upd.message.text
        users_to_loc = self.__users.set_index(['user_id'])
        users_to_loc.loc[chat_id].token = token
        self.__users = users_to_loc.reset_index()
        self.print_ui(chat_id, "Записал😉")
        self.__users.to_csv('Users.csv')

    async def distribution(self, upd: UpdateObj):
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
        elif mes == "/limits":
            await self.get_limits(chat_id)
        elif mes == "/buy_limits":
            await self.buy_limit(chat_id)
        elif mes == "/sell_limits":
            await self.sell_limit(chat_id)
        elif mes == "/cancel_limits":
            await self.cancel_limit(chat_id)
        elif mes == "/get_figi":
            await self.get_figi(chat_id)
        elif mes == "/change_token":
            await self.change_token(chat_id)
        elif mes == "sell":
            await self.sell_paper(chat_id)
        elif mes == '/last_price':
            await self.last_price(chat_id)
        else:
            self.print_ui(chat_id, "Попробуй воспользоваться функциями из меню")

    async def _worker(self):
        while True:
            upd = await self.queue.get()
            chat_id = upd.message.chat.id
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

    async def add_token(self, user_id: int, token=0):
        self.__users = self.__users.append({'user_id': user_id, 'token': token}, ignore_index=True)
        print(self.__users)
        self.__users.to_csv('Users.csv')

    async def find_id(self, user_id: int):
        return any(self.__users.user_id == user_id)
