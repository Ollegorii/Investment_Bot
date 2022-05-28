import asyncio
import datetime
import os
from Controller import *
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
# from Bot import *


def run():
    loop = asyncio.get_event_loop()
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    bot = Controller("5205698417:AAFeZkm72W8qdzbaYNc_TjDmE2UxEmtWvpw", 1, gauth)
    try:
        loop.create_task(bot.start())
        print('bot started')
        loop.run_forever()
    except:
        print("\nstopping")
        loop.run_until_complete(bot.stop())
        print('bot stopped')

run()