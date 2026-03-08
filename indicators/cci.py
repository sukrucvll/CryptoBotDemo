import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd

import numpy as np
from binance.client import Client
from storage.mongo_db import get_db,hata_kaydet
import time

class CCI:
    
    def __init__(self, name,zaman_dilimi,period):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period
        


    def cci_hesaplama_islem_md(self,df):
         
        try:
            df['TP'] = (df['yuksek'] + df['dusuk'] + df['kapanis']) / 3

            df['SMA_TP'] = df['TP'].rolling(window=self.period).mean()
            
            df['MAD'] = df['TP'].rolling(window=self.period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)

            df['CCI'] = (df['TP'] - df['SMA_TP']) / (0.015 * df['MAD'])

            
            df['SMA_TP14'] = df['TP'].rolling(window=14).mean()
            
            df['MAD_14'] = df['TP'].rolling(window=14).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)

            df['CCI_14'] = (df['TP'] - df['SMA_TP14']) / (0.015 * df['MAD_14'])
            df['CCI_EMA20'] = df['CCI'].ewm(span=20, adjust=False).mean()
            df['CCI_SMA20'] = df['CCI'].rolling(window=20).mean()
            df['CCI_SMA14'] = df['CCI_14'].rolling(window=14).mean()

            df.drop(columns=['TP', 'SMA_TP', 'MAD' , 'SMA_TP14', 'MAD_14'], inplace=True)

            return df
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"cci_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df