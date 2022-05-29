from BotUser import *

from typing import Optional


import aiohttp

from dcs import GetUpdatesResponse, SendMessageResponse


class TgUser(BotUser):
    def __init__(self, bot_id):#допилить наследование, написать super
        super().__init__(bot_id)

    def get_url(self, method: str):
        return f"https://api.telegram.org/bot{self.bot_id}/{method}"

    async def get_me(self) -> dict:
        url = self.get_url("getMe")
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.json()

    async def get_updates(self, offset: Optional[int] = None, timeout: int = 0) -> dict:
        url = self.get_url("getUpdates")
        params = {}
        if offset:
            params['offset'] = offset
        if timeout:
            params['timeout'] = timeout
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as resp:
                return await resp.json()

    async def get_updates_in_objects(self, offset: Optional[int] = None, timeout: int = 0) -> GetUpdatesResponse:
        res_dict = await self.get_updates(offset=offset, timeout=timeout)
        return GetUpdatesResponse.Schema().load(res_dict)

    async def send_message(self, chat_id: int, text: str) -> object:
        url = self.get_url("sendMessage")
        payload = {
            'chat_id': chat_id,
            'text': text
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)

    async def send_photo(self, chat_id: int, photo_url: str) -> object:
        url = self.get_url("sendPhoto")
        payload = {
            'chat_id': chat_id,
            'photo': photo_url,
            #'caption' : "Фоточка, а на ней красоточка",
            'parse_mode': 'Markdown',
            'disable_web_page_preview': 'true',
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                res_dict = await resp.json()
                return SendMessageResponse.Schema().load(res_dict)