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
        print(stringToLog+"\n\n")
        self.logFile.write(stringToLog)

   # def __del__(self):
   #     self.logFile.close()


class Stocker(Logger):
    portfolio_ = []
    local_demographic_ = []

    def _initialize_portfolio(self, data):
        self.portfolio_ = pd.DataFrame()
        self.portfolio_ = pd.DataFrame({'Stock' : [data.loc[0, 'Stock']], 'Transaction Amount' : [data.loc[0, 'Cost Price']], 'Remaining Units' : [data.loc[0, 'Units']], 'Average': [data.loc[0, 'Price']]})
        for i in range(1, len(data)):
            if(data.loc[i, 'Stock'] not in self.portfolio_.values):
                self.log("{} New Stock added to portfolio, Creating new entry in hash".format(data.loc[i, 'Stock']))
                self.portfolio_.loc[len(self.portfolio_.index)] = [data.loc[i, 'Stock'], data.loc[i, 'Cost Price'], data.loc[i, 'Units'], data.loc[i, 'Price']]
            else:
                if(data.loc[i, 'Transaction']=='B'):
                    self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Average'] += data.loc[i, 'Price']
                    self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Average'] /= 2
                    self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Transaction Amount'] += data.loc[i, 'Cost Price']
                    self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Remaining Units'] = self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Transaction Amount'] / self._get_market_price(data.loc[i, 'Stock']) * 1.0;
                    self.log("BUY: Total amount invested YTD in {} is {}".format(data.loc[i, 'Stock'], self.portfolio_.loc[self.portfolio_["Stock"]==data.loc[i, 'Stock'], "Transaction Amount"].iloc[0]))
                else:
                    self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Transaction Amount'] -= data.loc[i, 'Cost Price']
                    self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Remaining Units'] = self.portfolio_.loc[self.portfolio_['Stock'] == data.loc[i, 'Stock'], 'Transaction Amount'] / self._get_market_price(data.loc[i, 'Stock']) * 1.0;
                    self.log("SELL: Total amount invested YTD in {} is {}".format(
                        data.loc[i, 'Stock'],
                        self.portfolio_.loc[self.portfolio_["Stock"]==data.loc[i, 'Stock'], "Transaction Amount"].iloc[0]))

    
    def _get_market_price(self, asset_name):
        temp = yf.Ticker(asset_name)
        self.log("{} : Reading stock {} at {} ".format(datetime.datetime.utcnow(), asset_name, threading.currentThread().getName))
        return temp.info['regularMarketPrice']

    def _collate_buy_and_sell_transactions(self):
        self.log("{} Collating sell and buy transactions".format(datetime.datetime.utcnow()));
        self._initialize_portfolio(self.local_demographic_)

    def deduce_profits(self):
        sum = 0
        for i in range(0, len(self.portfolio_)):
            sum += self.portfolio_.loc[i, 'Transaction Amount']
        if sum < 0:
            self.log("may-day: Portfolio is in loss")
        else:
            self.log("woo-hoo, making money with Rs. {} in stocks".format(self.portfolio_["Transaction Amount"].sum()))


    def get_stock_demographics(self, file_input_df):
        self.local_demographic_ = file_input_df
        for i in range(0, len(file_input_df['Stock']), 1):
            self.local_demographic_.loc[i, 'CMP'] = self._get_market_price(self.local_demographic_.loc[i,'Stock'])
            self.local_demographic_.loc[i, 'Cost Price'] = self.local_demographic_.loc[i,'Price'] * self.local_demographic_.loc[i,'Units']
            self.local_demographic_.loc[i, 'Profits/Loss ETD'] = self.local_demographic_.loc[i,'CMP'] * self.local_demographic_.loc[i,'Units'] - self.local_demographic_.loc[i,'Cost Price']
            self.local_demographic_.loc[i, 'Percentage Change'] = str(self.local_demographic_.loc[i, 'Profits/Loss ETD'] / self.local_demographic_.loc[i,'Cost Price'] * 100) + str(' %')
        self._collate_buy_and_sell_transactions()
        self.deduce_profits()
        return self.local_demographic_

    def __init__(self, data):
        Logger.__init__(self, fileName= 'stocker_'+str(time.time()))

    def __del__(self):
        print(self.portfolio_)
    

class FileHandler(Logger):

    def __init__(self):
        Logger.__init__(self, fileName='file_'+str(time.time()))

    def read_user_file(self, file_path):
        self.log("{} : Reading file {} at {}".format(datetime.datetime.utcnow(), file_path, threading.currentThread().getName))
        df = pd.read_csv(file_path)
        return df

    def write_user_file(self, data):
        data.to_csv('derived_.csv', mode='w+', header=False)

    #def dict_of_stocks_bought(self, dataframe):

class Marketeer():
    def main():
        file_handler = FileHandler()
        data = file_handler.read_user_file('stock_err.csv')
        stocker = Stocker(data)
        _local_demographics_ = stocker.get_stock_demographics(data)
        file_handler.write_user_file(_local_demographics_)
        print(_local_demographics_)
        
    if __name__ == "__main__":
        main()
        

