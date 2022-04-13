from Logic import *
from User import *
from tinkoff.invest import Client, RequestError, PortfolioResponse, PositionsResponse, PortfolioPosition
import matplotlib.pyplot as plt
SANDBOX_TOKEN = "t.Zx3k_Kx4AoPerZe11E7JRSyuWijNSQ-BClojho6m7PgGsUrVY1FVXk9ayjZV64egufFQZ_DLlpTmFilYPh4y7g"

#b_id = broker_account_id = log.get_sync_client().register_sandbox_account(
#            ti.SandboxRegisterRequest(broker_account_type=ti.BrokerAccountType.tinkoff)
#        ).payload.broker_account_id
#print(b_id)
#print(stocks)
#log.deposit_rub(100000)
#tmp = c.get_market_bonds().payload
#print(tmp)
#log.buy(1, 'BBG00PNLY692')
#log.sell()
#print(c.get_portfolio().payload)
#id = ti.get_broker_account_id()
#print(id)
with Client(SANDBOX_TOKEN) as client:
    us = User(SANDBOX_TOKEN, client)
    #us.deposit_usd(563.32)
    #print(client.sandbox.get_sandbox_portfolio(account_id=us.get_account_id()))
    #print(us.buy(us.get_account_id(), 'BBG004730ZJ9', 1))
    #print(client.sandbox.get_sandbox_order_state(account_id=us.get_account_id(), order_id='31ea8257-da51-451d-92fa-c42a26744274'))
    #us.sell(us.get_account_id(), 'BBG004730ZJ9', 1)
    print(us.get_portfolio(us.get_account_id()))
    print(us.get_orders(us.get_account_id()))
    #print(client.instruments.shares())
    print(us.search('BBG002BC7WC5'))
    r = us.get_candels('BBG002BC7WC5').candles
    df = us.create_df(r)
    ax = df.plot(x='time', y='close')
    plt.show()
    #SPBXM
    #BBG002BC7WC5