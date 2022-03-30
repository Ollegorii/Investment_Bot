import Instrument
import VkInterface
import TgInterface


class Stonk(Instrument, VkInterface, TgInterface):
    def __init__(self, amount, figi):
        self.__amount = amount
        self.__figi = figi

    def draw(self):
        pass

    def Tg_draw(self):
        pass

    def Vk_draw(self):
        pass

