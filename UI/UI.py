from TgUser import *
from dcs import UpdateObj


class UI:
    def __init__(self, token: str):
        self.__tg_user = TgUser(token)

    async def print(self, chat_id: int, txt: str, mes_id):
        print(txt, mes_id)
        if mes_id == 0:
            await self.__tg_user.send_message(chat_id, txt)
        elif mes_id == 1:
            await self.__tg_user.send_photo(chat_id, txt)