from queue import Queue

from Logic import *
from TgUser import *
from Poller import *
from UI import *
from dcs import UpdateObj


class Controller:
    def __init__(self, token: str, n: int):
        self.__queue = asyncio.Queue()
        self.__UI_queue = asyncio.Queue()
        self.__logic = Logic(self.__UI_queue, self.__queue, n, gauth = GoogleAuth())
        self.__poller = Poller(token, self.__queue)
        self.__ui = UI(token)

    async def contr_cycle(self):
        while True:
            upd = await self.__UI_queue.get()
            chat_id = upd[0]
            txt = upd[1]
            if txt != "":
                await self.print_ui(chat_id, txt)

    async def start(self):
        await self.__poller.start()
        await self.__logic.start()
        await self.contr_cycle()

    async def stop(self):
        await self.__poller.stop()
        await self.__logic.stop()

    async def print_ui(self, chat_id: int, txt: str):
        await self.__ui.print(chat_id, txt)