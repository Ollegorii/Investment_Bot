from Instrument import *
from VkInterface import *
from TgInterface import *


class Stock(Instrument, VkInterface, TgInterface):
    def __init__(self, amount, name, figi):
        super().__init__()
        self.__amount = amount
        self.__name = name
        self.__figi = figi

    def Tg_draw(self):
        pass

    def Vk_draw(self):
        pass

    def get_money(self):
        return "lots: " + str(self.__amount), self.__name



