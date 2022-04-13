import numpy as np
import pandas as pd


class Logic:
    def __init__(self, use_sandbox=True):
        self.__users = pd.read_csv('Users.csv', usecols=['user_id', 'token'])

    def add(self, user_id, token=0):
        self.__users = self.__users.append({'user_id': user_id, 'token': token}, ignore_index=True)
        print(self.__users)
        # self.__users.to_csv('Users.csv')

    def find_id(self, user_id):
        return any(self.__users.user_id == user_id)
