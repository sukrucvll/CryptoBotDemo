import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import numpy as np
from binance.client import Client
from storage.mongo_db import get_db,hata_kaydet
import time



class MACD:
    
    def __init__(self, name,zaman_dilimi,period_ema,period_ema2):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period_ema = period_ema
        self.period_ema2 = period_ema2
        
    

    def macd_hesaplama_islem_md(self,df):
         
        try:
            df['ema12'] = df['kapanis'].ewm(span=self.period_ema, adjust=False).mean()
            df['ema26'] = df['kapanis'].ewm(span=self.period_ema2, adjust=False).mean()
            df['ema9'] = df['kapanis'].ewm(span=9, adjust=False).mean()
            df['ema20'] = df['kapanis'].ewm(span=20, adjust=False).mean()
            df['ema50'] = df['kapanis'].ewm(span=50, adjust=False).mean()
            df['macd'] = df['ema12'] - df['ema26']
            df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['histogram'] = df['macd'] - df['signal']
            df['dusus']=(df['macd']<0)
            df['yukselis']=(df['macd']>0)
            df.drop(columns=['ema12','ema26','macd','signal'],inplace=True)
            
            return df
        
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"macd_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df




    