from TgUser import *
from dcs import UpdateObj


class UI:
    def __init__(self, token: str):
        self.__bot_user = TgUser(token)

    async def print(self, chat_id: int, txt: str, mes_id: int):
        if mes_id == 0:
            await self.__bot_user.send_message(chat_id, txt)
        elif mes_id == 1:
            await self.__bot_user.send_photo(chat_id, txt)