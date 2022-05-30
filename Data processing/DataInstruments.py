import pandas as pd
class DataInstruments:
    def __init__(self, client):
        self.__dict = {'FG0000000000': 'Рубль'}
        self.__figi_cur = {'FG0000000000': 'rub'}
        self.__currencies = [c.figi for c in client.instruments.currencies().instruments]
        it = [client.instruments.currencies().instruments, client.instruments.shares().instruments,
              client.instruments.bonds().instruments, client.instruments.etfs().instruments, client.instruments.futures().instruments]
        for i in range(len(it)):
            for cur in it[i]:
                self.__dict[cur.figi] = cur.name
                self.__figi_cur[cur.figi] = cur.currency
        self.__data = pd.DataFrame(list(self.__dict.items()), columns = ['Figi', 'Name'])
        self.__data = self.__data.set_index('Figi')

    def get_data(self):
        return self.__data

    def get_dict(self):
        return self.__dict

    def get_currencies(self):
        return self.__currencies

    def get_figi_cur(self):
        return self.__figi_cur