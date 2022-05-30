import mplfinance as mpf
from decimal import Decimal
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition, OrderDirection, OrderType, MoneyValue, Quotation, InstrumentIdType, CandleInterval, HistoricCandle
from tinkoff.invest.services import Services
from tinkoff.invest.services import SandboxService
import pandas as pd
from datetime import datetime, timedelta
from DataInstruments import *
from Errors import *
import dataframe_image as dfi
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os
from Plot import *
import time
# Сброс ограничений на количество выводимых рядов
pd.set_option('display.max_rows', None)

# Сброс ограничений на число столбцов
pd.set_option('display.max_columns', None)

# Сброс ограничений на количество символов в записи
pd.set_option('display.max_colwidth', None)

#def GenerateFileOfInstruments(client):

class User:
    def __init__(self, token : str, client : Client, GD, use_sandbox=True, market = "Tinkoff"):
        self.__token = token
        self.__use_sandbox = use_sandbox
        self.__accounts = []
        self.__client = client
        self.__account_id = None
        self.__market = market
        self.__data : DataInstruments = DataInstruments(client)
        self.__gauth = GD.get_gauth()
        self.__files = []
        self.__plot = Plot('candles')
        self.__GD = GD

    def get_accounts(self):
        """
        Получаю все аккауты, пока что ограничимся одним
        """
        if self.__market == "Tinkoff":
            if len(self.__accounts) == 0:
                self.__client.sandbox.open_sandbox_account()
                acc = self.__client.sandbox.get_sandbox_accounts()
                self.__accounts.append(acc)
            return self.__accounts
        elif self.__market == "Vtb":
            pass

    def create_account(self):
        '''
        Создание аккаунта
        '''
        acc = self.__client.sandbox.open_sandbox_account()
        self.__accounts.append(acc)


    def get_account_id(self):
        """
        Получаю id первого аккаунта в песочнице
        """
        if self.__market == "Tinkoff":
            if (self.__account_id == None):
                acc = self.get_accounts()
                self.__account_id = acc[0].accounts[0].id
            return self.__account_id
        elif self.__market == "Vtb":
            pass

    def __m_val_to_cur(self, q):
        '''
        Перевожу величину класса MoneyValue в величину в рублях
        для Tinkoff
        '''
        u = q.units
        n = q.nano
        return u + n / 1e9

    def __portfolio_pose_todict(self, p: PortfolioPosition):
        '''
        Перевожу объект класса PortfolioPosition в словарь для формирования DataFrame в дальнейшем
        для Tinkoff
        '''
        name = self.__data.get_data().loc[p.figi].Name
        r = {
            'Name' : name,
            'figi': p.figi,
            'quantity': self.__m_val_to_cur(p.quantity),
            'instrument_type': p.instrument_type,
            'currency': p.average_position_price.currency,
            'exp_yield': self.__m_val_to_cur(p.expected_yield),
        }
        return r

    def __amount_to_quanity(self, amount):
        '''
        Перевод числа в метрику класса Quotation
        для Tinkoff
        '''
        u = int(amount)
        n = int((amount - int(amount)) * 1e9)
        return [u, n]

    def deposit_rub(self, amount):
        '''
        Пополняю счет рублями
        '''
        if self.__market == "Tinkoff":
            q = self.__amount_to_quanity(amount)
            self.__client.sandbox.sandbox_pay_in(account_id=self.get_account_id(),
                                                 amount = MoneyValue(currency='rub', units=q[0], nano=q[1]))
        elif self.__market == "Vtb":
            pass

    def deposit_usd(self, amount):
        '''
        Пополняю счет долларами
        '''
        if self.__market == "Tinkoff":
            q = self.__amount_to_quanity(amount)
            self.__client.sandbox.sandbox_pay_in(account_id=self.get_account_id(),
                                                 amount=MoneyValue(currency='usd', units=q[0], nano=q[1]))
        elif self.__market == "Vtb":
            pass

    def get_portfolio(self, account_id):
        '''
        Получаю все бумаги в портфеле
        '''
        if self.__market == "Tinkoff":
            p = self.__client.sandbox.get_sandbox_portfolio(account_id=account_id).positions
            df = pd.DataFrame([self.__portfolio_pose_todict(pos) for pos in p])
            df = df.set_index('Name')
            return df
        elif self.__market == "Vtb":
            pass

    def buy(self, account_id, figi, amount):
        '''
        Покупаю бумагу по фиги
        '''
        if self.__market == "Tinkoff":
            dict = self.__data.get_dict()
            if figi not in dict:
                raise FigiError
            try:
                r = self.__client.sandbox.post_sandbox_order(
                    figi=figi,
                    quantity=amount,
                    account_id=account_id,
                    order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
            except:
                raise AmountError
        elif self.__market == "Vtb":
            pass

    def sell(self, account_id, figi, amount):
        '''
        Продажа бумаги по figi
        '''
        if self.__market == "Tinkoff":
            dict = self.__data.get_dict()
            if figi not in dict:
                raise FigiError
            try:
                r = self.__client.sandbox.post_sandbox_order(
                    figi=figi,
                    quantity=amount,
                    account_id=account_id,
                    order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_MARKET
                )
            except:
                raise AmountError
        elif self.__market == "Vtb":
            pass

    def buy_limit(self, account_id, figi, amount, price):
        '''
        Лимитная покупка по figi
        '''
        if self.__market == "Tinkoff":
            dict = self.__data.get_dict()
            if figi not in dict:
                raise FigiError
            try:
                q = self.__amount_to_quanity(price)
                r = self.__client.sandbox.post_sandbox_order(
                    figi=figi,
                    quantity=amount,
                    price=Quotation(units=q[0], nano=q[1]),
                    account_id=account_id,
                    order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
                    direction=OrderDirection.ORDER_DIRECTION_BUY,
                    order_type=OrderType.ORDER_TYPE_LIMIT
                )
            except:
                raise AmountError
        elif self.__market == "Vtb":
            pass

    def sell_limit(self, account_id, figi, amount, price):
        '''
        Лимтная продажа по figi
        '''
        if self.__market == "Tinkoff":
            dict = self.__data.get_dict()
            if figi not in dict:
                raise FigiError
            try:
                q = self.__amount_to_quanity(price)
                r = self.__client.sandbox.post_sandbox_order(
                    figi=figi,
                    quantity=amount,
                    price=Quotation(units=q[0], nano=q[1]),
                    account_id=account_id,
                    order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
                    direction=OrderDirection.ORDER_DIRECTION_SELL,
                    order_type=OrderType.ORDER_TYPE_LIMIT
                )
            except:
                raise AmountError
        elif self.__market == "Vtb":
            pass

    def cancel_order(self, account_id, order_id):
        '''
        Отмена заявки
        '''
        if self.__market == "Tinkoff":
            return self.__client.sandbox.cancel_sandbox_order(account_id=account_id, order_id=order_id)
        elif self.__market == "Vtb":
            pass


    def get_orders(self, account_id):
        '''
        Получение всех активных заявок
        '''
        if self.__market == "Tinkoff":
            orders = self.__client.sandbox.get_sandbox_orders(account_id=account_id).orders
            if len(orders) != 0:
                d = []
                for ord in orders:
                    #if (ord.figi in self.__data.get_currencies()):
                    #   continue
                    d.append({
                    'Lots': ord.lots_requested,
                    'Price': self.__m_val_to_cur(ord.initial_order_price),
                    'Currency': ord.initial_order_price.currency,
                    'Name': self.__data.get_data().loc[ord.figi].Name,
                    'Type':  'Buy' if ord.direction == OrderDirection.ORDER_DIRECTION_BUY else 'Sell'
                    })
                df = pd.DataFrame(d)
                if df.size != 0:
                    df = df.set_index('Name')
                    return df
            else:
                raise EmptyData
        elif self.__market == "Vtb":
            pass

    def cancel_order_by_number(self, account_id, number):
        '''
        Отмена заявки по порядковому номеру
        '''
        if self.__market == "Tinkoff":
            df = self.get_orders(account_id=account_id)
            orders = self.__client.sandbox.get_sandbox_orders(account_id=account_id).orders
            if number > len(orders):
                raise InputError
            else:
                order_id = orders[number - 1].order_id
                self.__client.sandbox.cancel_sandbox_order(account_id=account_id, order_id=order_id)
        elif self.__market == "Vtb":
            pass

    def close_account(self, account_id):
        '''
        Закрытие счета
        '''
        if self.__market == "Tinkoff":
            return self.__client.sandbox.close_sandbox_account(account_id=account_id)
        elif self.__market == "Vtb":
            pass

    def __create_df_candles(self, candles: [HistoricCandle]):
        if self.__market == "Tinkoff":
            df = pd.DataFrame([{
                'Date': c.time,
                'open': self.__m_val_to_cur(c.open),
                'high': self.__m_val_to_cur(c.high),
                'low': self.__m_val_to_cur(c.low),
                'close': self.__m_val_to_cur(c.close),
                'volume': c.volume,
            } for c in candles])
            df = df.set_index('Date')
            return df
        if self.__market == "Vtb":
            pass

    def get_candles(self, figi, day_int = 7):
        '''
        Получаю свечной график
        '''
        r = []
        if self.__market == "Tinkoff":
            if figi not in self.__data.get_dict():
                raise FigiError
            param = 0
            if day_int > 7:
                param = CandleInterval.CANDLE_INTERVAL_DAY
            elif  day_int <= 7 and day_int > 1:
                param = CandleInterval.CANDLE_INTERVAL_HOUR
            elif day_int <= 1:
                param = CandleInterval.CANDLE_INTERVAL_15_MIN
            r = self.__client.market_data.get_candles(
                figi=figi,
                from_=datetime.utcnow() - timedelta(days=day_int),
                to=datetime.utcnow(),
                interval=param
            )
            df = self.__create_df_candles(r.candles)
            #mpf.plot(df, type='candle', mav=(10, 20, 40), savefig='candels.png')
            self.__plot.plot_candles(df)
            url = self.__png_to_url()
            return url
        elif self.__market == "Vtb":
            pass

    def get_all_figies(self):
        '''
        Получение всех figi
        '''
        self.__data.get_data().to_csv('figies.csv')
        url = self.__GD.upload('figies.csv')
        return url

    def df_to_url(self, df: pd.DataFrame):
        '''
        Получение изображения DataFrame и получение ссылки на него в облаке
        '''
        #self.__gauth.LocalWebserverAuth()
        dfi.export(df, 'mytable.png', max_rows=-1)
        filename = 'mytable.png'
        url = self.__GD.upload(filename)
        #url = url[:len(url) - 16]
        return url

    def __png_to_url(self, filename = 'candles.png'):
        url = self.__GD.upload(filename)
        return url

    def get_last_price(self, figi):
        if figi not in self.__data.get_dict():
            raise FigiError
        else:
            r = self.__client.market_data.get_last_prices(figi=[figi])
            q = r.last_prices[0].price
            currency = self.__data.get_figi_cur()[figi]
            val = self.__m_val_to_cur(q)
            c = '$' if currency == 'usd' else '₽'
            return f'{val} {c}'
