import sys
import os

# Proje klasörünü import yoluna ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import requests
import numpy as np
from binance.client import Client
from  api.binance_ import bagla
from storage.mongo_db import get_db
import ta 
import time
import ulitis.coin_isim 
import storage.mysql_db 
from storage.mongo_db import hata_kaydet


class RSI:
    
    def __init__(self, name,zaman_dilimi,period):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period
        
    

    def rsi_hesaplama_islem_md(self,df):

          rsi_values = self.calculate_rsi(df['kapanis'], period=self.period,name=self.name)

          df['RSI'] = rsi_values
     
          return df

        
    
    @staticmethod
    def calculate_rsi(close_prices, period=10,name=''):
        try:

            delta = close_prices.diff()
            

            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
            avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
           

            return rsi
        except Exception as e:
            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"RSI hesaplanırken '{name}' için hata oluştu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return None
