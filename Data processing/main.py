from Logic import *
from User import *
import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
SANDBOX_TOKEN = "t.Zx3k_Kx4AoPerZe11E7JRSyuWijNSQ-BClojho6m7PgGsUrVY1FVXk9ayjZV64egufFQZ_DLlpTmFilYPh4y7g"

# df = pd.DataFrame({
#     'user_id': 845,
#     'token': 34,
# })
# print(df)
#users = pd.read_csv('Users.csv')
#t="""user_id,token"""
#users = pd.read_csv(io.StringIO(t))
#users1 = users.set_index(['user_id'])
users = pd.DataFrame({'user_id':[0], 'token':[0]})
print(users)
print(users)
users = users.append({'user_id': 543, 'token': 546}, ignore_index=True)
print(users)
users = users.set_index(['user_id'])
print(users.loc[543])
#print(any(users.loc[543]))
df = pd.DataFrame({'value':np.random.random(10000), 'key':range(100, 10100)})
print(df.head())
df_with_index = df.set_index(['key'])
print(df_with_index.head())
print(df_with_index.loc[10099])