from Logic import *
SANDBOX_TOKEN = "t.Zx3k_Kx4AoPerZe11E7JRSyuWijNSQ-BClojho6m7PgGsUrVY1FVXk9ayjZV64egufFQZ_DLlpTmFilYPh4y7g"
log = Logic([], SANDBOX_TOKEN, use_sandbox=True)
c = log.get_sync_client()
print(log.get_broker_account_id())

bonds = c.get_market_bonds()

etfs = c.get_market_etfs()

stocks = c.get_market_stocks()
print(etfs)
#log.deposit_rub(100000)
#tmp = c.get_market_bonds().payload
#print(tmp)
#log.buy(1, 'BBG00PNLY692')
#log.sell()
print(c.get_portfolio().payload)
#id = ti.get_broker_account_id()
#print(id)


