from Instrument import *
from VkInterface import *
from TgInterface import *


class Cash(Instrument, VkInterface, TgInterface):
    def __init__(self, amount, currency):
        super().__init__()
        self.__amount = amount
        self.__currency = currency

    def Tg_draw(self):
        pass

    def Vk_draw(self):
        pass

    def get_money(self):
        return int(self.__amount), str(self.__currency)
