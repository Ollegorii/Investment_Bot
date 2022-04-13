from Cash import *
from Stock import *
from decimal import Decimal
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition, \
    OrderDirection, OrderType, MoneyValue, Quotation, InstrumentIdType, CandleInterval, HistoricCandle
from tinkoff.invest.services import Services
from tinkoff.invest.services import SandboxService
import pandas as pd
from datetime import datetime, timedelta

# Сброс ограничений на количество выводимых рядов
pd.set_option('display.max_rows', None)

# Сброс ограничений на число столбцов
pd.set_option('display.max_columns', None)

# Сброс ограничений на количество символов в записи
pd.set_option('display.max_colwidth', None)


class User:
    def __init__(self, token, client: Services, use_sandbox=True):
        self.__token = token
        self.__use_sandbox = use_sandbox
        self.__client = client
        self.__accounts = []
        self.__account_id = None
        self.__instruments = []

    def update_instruments(self, account_id):
        """
        Обновление списка instruments в соответсвии с портфелем
        """
        p = self.__client.sandbox.get_sandbox_portfolio(account_id=account_id).positions
        self.__instruments = []
        for i in range(len(p)):
            if p[i].instrument_type == 'currency':
                self.__instruments.append(
                    Cash(self.__m_val_to_curr(p[i].quantity), p[i].average_position_price.currency))
            if p[i].instrument_type == 'share':
                self.__instruments.append(Stock(p[i].quantity, p[i].current_price, p[i].figi))

    def get_accounts(self):
        """
        Получаю все аккаунты, пока что ограничимся одним
        """
        if len(self.__accounts) == 0:
            self.__client.sandbox.open_sandbox_account()
            acc = self.__client.sandbox.get_sandbox_accounts()
            self.__accounts.append(acc)

        return self.__accounts

    def get_account_id(self):
        """
        Получаю id первого аккаунта в песочнице
        """
        if (self.__account_id == None):
            acc = self.get_accounts()
            self.__account_id = acc[0].accounts[0].id
        return self.__account_id

    def __m_val_to_curr(self, q):
        '''
        Перевожу величину класса MoneyValue в величину в рублях
        '''
        u = q.units
        n = q.nano
        return u + n / 1e9

    def __portfolio_pose_todict(self, p: PortfolioPosition):
        '''
        Перевожу объект класса PortfolioPosition в словарь для формирования DataFrame в дальнейшем
        '''
        r = {
            'figi': p.figi,
            'quantity': self.__m_val_to_curr(p.quantity),
            'expected_yield': self.__m_val_to_curr(p.expected_yield),
            'instrument_type': p.instrument_type,
            'average_buy_price': self.__m_val_to_curr(p.average_position_price),
            'currency': p.average_position_price.currency,
            'nkd': self.__m_val_to_curr(p.current_nkd),
        }
        return r

    def __amount_to_quanity(self, amount):
        '''
        Перевод числа в метрику класса Quotation
        '''
        u = int(amount)
        n = int((amount - int(amount)) * 1e9)
        return [u, n]

    def deposit_rub(self, amount):
        '''
        Пополняю счет рублями
        '''
        q = self.__amount_to_quanity(amount)
        self.__client.sandbox.sandbox_pay_in(account_id=self.get_account_id(),
                                             amount=MoneyValue(currency='rub', units=q[0], nano=q[1]))

    def deposit_usd(self, amount):
        '''
        Пополняю счет долларами
        '''
        q = self.__amount_to_quanity(amount)
        self.__client.sandbox.sandbox_pay_in(account_id=self.get_account_id(),
                                             amount=MoneyValue(currency='usd', units=q[0], nano=q[1]))

    def get_portfolio(self, account_id):
        '''
        Получаю все бумаги в портфеле
        '''
        p = self.__client.sandbox.get_sandbox_portfolio(account_id=account_id).positions
        df = pd.DataFrame([self.__portfolio_pose_todict(pos) for pos in p])
        return df

    def buy(self, account_id, figi, amount):
        '''
        Покупаю бумагу по фиги
        '''
        r = self.__client.sandbox.post_sandbox_order(
            figi=figi,
            quantity=amount,
            account_id=account_id,
            order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
            direction=OrderDirection.ORDER_DIRECTION_BUY,
            order_type=OrderType.ORDER_TYPE_MARKET
        )
        return r

    def sell(self, account_id, figi, amount):
        '''
        Продажа бумаги по figi
        '''
        r = self.__client.sandbox.post_sandbox_order(
            figi=figi,
            quantity=amount,
            account_id=account_id,
            order_id=datetime.now().strftime("%Y-%m-%dT %H:%M:%S"),
            direction=OrderDirection.ORDER_DIRECTION_SELL,
            order_type=OrderType.ORDER_TYPE_MARKET
        )
        return r

    def buy_limit(self, account_id, figi, amount, price):
        '''
        Лимитная покупка по figi
        '''
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
        return r

    def sell_limit(self, account_id, figi, amount, price):
        '''
        Лимтная продажа по figi
        '''
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
        return r

    def cancel_order(self, account_id, order_id):
        '''
        Отмена заявки
        '''
        return self.__client.sandbox.cancel_sandbox_order(account_id=account_id, order_id=order_id)

    def get_orders(self, account_id):
        '''
        Получение всех активных заявок
        '''
        return self.__client.sandbox.get_sandbox_orders(account_id=account_id)

    def close_account(self, account_id):
        '''
        Закрытие счета
        '''
        return self.__client.sandbox.close_sandbox_account(account_id=account_id)

    def search(self, figi):
        return self.__client.instruments.share_by(id=figi, id_type=InstrumentIdType.INSTRUMENT_ID_TYPE_FIGI)

    def get_candels(self, figi):
        r = self.__client.market_data.get_candles(
            figi=figi,
            from_=datetime.utcnow() - timedelta(days=7),
            to=datetime.utcnow(),
            interval=CandleInterval.CANDLE_INTERVAL_HOUR  # см. utils.get_all_candles
        )
        return r

    def create_df(self, candles: [HistoricCandle]):
        df = pd.DataFrame([{
            'time': c.time,
            'volume': c.volume,
            'open': self.__m_val_to_curr(c.open),
            'close': self.__m_val_to_curr(c.close),
            'high': self.__m_val_to_curr(c.high),
            'low': self.__m_val_to_curr(c.low),
        } for c in candles])

        return df

    def get_instruments(self):
        return self.__instruments

    def print_cash(self):
        for x in self.get_instruments():
            print(x.get_money())
