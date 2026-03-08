import sys
import os

# Proje klasörünü import yoluna ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import numpy as np
from binance.client import Client
from storage.mongo_db import get_db,hata_kaydet
import time
 


class TRIX:
    
    def __init__(self, name,zaman_dilimi,period_trix):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period_trix = period_trix

    def trix_hesaplama_islem_md(self,df):
        try:
  
            df['ema1'] = df['kapanis'].ewm(span=self.period_trix, adjust=False).mean()

            df['ema2'] = df['ema1'].ewm(span=self.period_trix, adjust=False).mean()

            df['ema3'] = df['ema2'].ewm(span=self.period_trix, adjust=False).mean()
            
            df['trix'] = (df['ema3'] - df['ema3'].shift(1)) / df['ema3'].shift(1) * 10000 

            df['trix_dusus'] = df['trix'] < 0
            df['trix_yukselis'] = df['trix'] > 0

            df.drop(columns=['ema1','ema2','ema3'], inplace=True)

            return df
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
                
            hata = {
                    'hata': str(e),
                    'aciklama': f"trix_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                    'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df  



    