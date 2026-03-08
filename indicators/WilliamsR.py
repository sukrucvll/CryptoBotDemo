import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import requests
import numpy as np
from binance.client import Client
from storage.mongo_db import get_db,hata_kaydet
import time



class WILR:
    
    def __init__(self, name,zaman_dilimi,period):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period
        

    def wil_r_hesaplama_islem_md(self,df):
        try:
          pd.set_option('display.float_format', lambda x: '%.8f' % x)

          df['en_yuksek']=df['yuksek'].rolling(window=self.period).max()
        
          df['en_dusuk']=df['dusuk'].rolling(window=self.period).min()
        

          df['wil_r']=(((df['en_yuksek']-df['kapanis'])/(df['en_yuksek']-df['en_dusuk']))*(-100))
          
          df.drop(columns=[ 'en_yuksek','en_dusuk'],inplace=True)

          return  df
        
        
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
                
            hata = {
                    'hata': str(e),
                    'aciklama': f"wil_r_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                    'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df 



         


 
    