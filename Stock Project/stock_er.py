import yfinance as yf
import numpy as np 
import pandas as pd 
import os
import threading
import time
import datetime
from pathlib import Path


class Logger(object):

    def __init__(self, path='logs/Stock', fileName="default"):
        Path(path).mkdir(mode = 0o777, parents=True, exist_ok=True)
        self.logFile = open(path + '/' + fileName + '.log', 'w+')
        self.logFile.seek(0, 2)

    def log(self, stringToLog):
        self.logFile.write(stringToLog)

   # def __del__(self):
   #     self.logFile.close()


class Stocker(Logger):

    def __init__(self):
        Logger.__init__(self, fileName= 'stocker_'+str(time.time()))
        
    def _get_market_price(self, asset_name):
        temp = yf.Ticker(asset_name)
        self.log("{} : Reading stock {} at {} ".format(datetime.datetime.utcnow(), asset_name, threading.currentThread().getName))
        return temp.info['regularMarketPrice']

    def get_stock_demographics(self, file_input_df):
        for i in range(0, len(file_input_df['Stock']), 1):
            file_input_df.loc[i,'CMP'] = self._get_market_price(file_input_df.loc[i,'Stock'])
            file_input_df.loc[i, 'Profits/Loss ETD'] = file_input_df.loc[i,'CMP'] - file_input_df.loc[i,'Price']
            file_input_df.loc[i, 'Percentage Change'] = str(file_input_df.loc[i, 'Profits/Loss ETD'] / file_input_df.loc[i,'Price'] * 100) + str(' %')
        return file_input_df



class FileHandler(Logger):

    def __init__(self):
        Logger.__init__(self, fileName='file_'+str(time.time()))

    def read_user_file(self, file_path):
        self.log("{} : Reading file {} at {}".format(datetime.datetime.utcnow(), file_path, threading.currentThread().getName))
        df = pd.read_csv(file_path)
        return df

    def write_user_file(self, file_path):
        print("Placeholder")

    #def dict_of_stocks_bought(self, dataframe):

class Marketeer():
    def main():
        stocker = Stocker()
        file_handler = FileHandler()
        _local_demographics_ = stocker.get_stock_demographics(file_handler.read_user_file('stock_err.csv'))
        print(_local_demographics_)
        
    if __name__ == "__main__":
        main()
        

