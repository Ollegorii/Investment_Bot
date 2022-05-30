from Logic import *
from User import *
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition
import matplotlib.pyplot as plt
from GDrive import *
SANDBOX_TOKEN = "t.Zx3k_Kx4AoPerZe11E7JRSyuWijNSQ-BClojho6m7PgGsUrVY1FVXk9ayjZV64egufFQZ_DLlpTmFilYPh4y7g"
with Client(SANDBOX_TOKEN) as client:
    GD = GDrive()
    us = User(SANDBOX_TOKEN, client, GD)
    #us.deposit_usd(563.32)
    #print(client.sandbox.get_sandbox_portfolio(account_id=us.get_account_id()))
    #us.sell(us.get_account_id(), 'BBG004730ZJ9', 1)
    id = us.get_account_id()
    #df = us.get_portfolio(us.get_account_id())
    #print(df)
    #print(client.instruments.shares())
    #print(us.search('BBG000BNSZP1')) #MacDonalds
    #us.buy_limit(account_id=id, figi='BBG0013HGFT4', amount=1, price=70)
    #us.sell_limit(account_id=id, figi='BBG004730ZJ9', amount=1, price=1)
    #us.sell(account_id=id, figi='BBG000BNSZP1', amount=1)
    '''
    try:
        us.cancel_order_by_number(account_id=id, number=2)
    except InputError:
        print('Номер запроса больше чем их кол-во')
    '''
    print(us.get_last_price('BBG004730ZJ9'))
    #us.buy(account_id=id, figi='BBG000BNSZP1', amount=1)
    #print(us.get_orders(account_id=id))
    #print(us.get_candles('BBG000BNSZP1', day_int=150))
    #us.get_all_figies()
    #print(GD.upload('figies.csv'))
    #GD.delete_file()
    #us.deleate_file()
    #client.market_data.get_last_prices('BBG000BNSZP1')
    #print(client.market_data.get_last_prices(figi=['BBG000BNSZP1']).last_prices[0].price)
    #us.buy(account_id=id, figi= 'BBG000BNSZP1', amount=1)
    #ax = df.plot(x='time', y='close')
    #us.cancel_order_by_number(account_id=id, number=3)
    #plt.show()
    #SPBXM
    #BBG002BC7WC5