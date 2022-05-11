from TgUser import *
from dcs import UpdateObj


class UI:
    def __init__(self, token: str):
        self.__tg_user = TgUser(token)

    async def print(self, chat_id: int, txt: str):
        await self.__tg_user.send_message(chat_id, txt)
