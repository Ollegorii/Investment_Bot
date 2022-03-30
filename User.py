import tinvest as ti
from Cash import *
from Stock import *


class User:
    def __init__(self, token):
        self.__token = token
        self.__client = ti.SyncClient(token, use_sandbox=True)
        stock = self.__client.get_portfolio()
        currency = self.__client.get_portfolio_currencies()
        self.__instruments = []
        for curr in currency.payload.currencies:
            self.__instruments.append(Cash(curr.balance, curr.currency[-3:]))
        for curr in stock.payload.positions:
            if curr.instrument_type == 'Stock':
                self.__instruments.append(Stock(curr.balance, curr.name, curr.figi))

    def get_instruments(self):
        return self.__instruments

    def print_cash(self):
        for x in self.get_instruments():
            print(x.get_money())