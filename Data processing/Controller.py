from queue import Queue
from Logic import *
from TgUser import *
from Poller import *
from UI import *
from dcs import UpdateObj

class Controller:
    def __init__(self, bot_token: str, n: int, GD):
        self.__queue = asyncio.Queue()
        self.__UI_queue = asyncio.Queue()
        self.__logic = Logic(self.__UI_queue, self.__queue, n, GD)
        self.__poller = Poller(bot_token, self.__queue)
        self.__ui = UI(bot_token)

    async def contr_cycle(self):
        while True:
            upd = await self.__UI_queue.get()
            chat_id = upd[0]
            txt = upd[1]
            mes_id = upd[2]
            if txt != "":
                await self.print_ui(chat_id, txt, mes_id)

    async def start(self):
        await self.__poller.start()
        await self.__logic.start()
        await self.contr_cycle()

    async def stop(self):
        await self.__poller.stop()
        await self.__logic.stop()

    async def print_ui(self, chat_id: int, txt: str, mes_id: int):
        await self.__ui.print(chat_id, txt, mes_id)