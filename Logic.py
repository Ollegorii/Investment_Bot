import tinvest as ti
from decimal import Decimal


class Logic:
    def __init__(self, users, token, use_sandbox=True):
        self.__users = users
        self.use_sandbox = use_sandbox
        self.broker_account_id = None
        self.token = token
        self.sync_client = None

    def get_sync_client(self):
        """
        Клиент для запросов к API
        """
        if not self.sync_client: self.sync_client = ti.SyncClient(self.token, use_sandbox=self.use_sandbox)
        return self.sync_client

    def get_broker_account_id(self):
        """
        Полдучаю broker_account_id для Песочницы
        """
        # проверка на работу в песочнице
        if not self.use_sandbox: raise Exception("Пока в Песочнице")

        # получаю список аккаунтов (в песочнице только 1 акк)
        if not self.broker_account_id:
            accounts = self.get_sync_client().get_accounts().payload.accounts
            self.broker_account_id = self.__create_sandbox() if len(accounts) <= 0 else accounts[0].broker_account_id

        return self.broker_account_id

    def delete_sandbox(self):
        """
        Удаление песочницы
        """
        accounts = self.get_sync_client().get_accounts().payload.accounts

        if len(accounts) > 0: self.get_sync_client().remove_sandbox_account(accounts[0].broker_account_id)

    def __create_sandbox(self):
        """
        Создание песочницы
        """

        # создаю аккаунт в песочнице и получаю его номер
        broker_account_id = self.get_sync_client().register_sandbox_account(
            ti.SandboxRegisterRequest(broker_account_type=ti.BrokerAccountType.tinkoff)
        ).payload.broker_account_id

        return broker_account_id

    def deposit_rub(self, amount):
        self.get_sync_client().set_sandbox_currencies_balance(
            ti.SandboxSetCurrencyBalanceRequest(balance=amount, currency=ti.SandboxCurrency('RUB'))
        )

    def deposit_usd(self, amount):
        self.get_sync_client().set_sandbox_currencies_balance(
            ti.SandboxSetCurrencyBalanceRequest(balance=amount, currency=ti.SandboxCurrency('USD'))
        )

    def __market_order(self, direction, lots, figi):
        """
        Рыночная заявка
        Песочница ничего не знает о рыночных котировках, поэтому все лимитные поручения сразу, без задержек, исполняются по цене, указанной в поручении.
        Все рыночные поручения исполняются по фиксированной цене в 100.
        """
        request = ti.MarketOrderRequest(lots=lots, operation=direction)
        resp = self.get_sync_client().post_orders_market_order(figi, request)
        return resp

    def __limit_order(self, direction, price, lots, figi):
        request = ti.LimitOrderRequest(lots=lots, operation=direction, price=Decimal(price))
        resp = self.get_sync_client().post_orders_limit_order(figi, request)
        return resp

    def buy(self, lots=1, figi='BBG0047315D0'):
        """
        ПОКУПКА бумаги по figi
        """
        return self.__market_order(ti.OperationType.buy, lots, figi)

    def sell(self, lots=1, figi='BBG0047315D0'):
        """
        ПРОДАЖА бумаги по figi
        """
        return self.__market_order(ti.OperationType.sell, lots, figi)

    def buy_limit(self, price: float, lots=1, figi='BBG0047315D0'):
        """
        Лимитная заявка на ПОКУПКУ,
        Песочница исполнит по любой цене, любой объем и сразу
        """
        return self.__limit_order(ti.OperationType.buy, price, lots, figi)

    def sell_limit(self, price: float, lots=1, figi='BBG0047315D0'):
        """
        Лимитная заявка на ПРОДАЖУ
        """
        return self.__limit_order(ti.OperationType.sell, price, lots, figi)
