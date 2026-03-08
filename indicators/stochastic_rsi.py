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

class STRSI:
    
    def __init__(self, name,zaman_dilimi,period_rsi,periot_stoph):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period_rsi = period_rsi
        self.periot_stoph = periot_stoph
        
    

    def si_rsi_hesaplama_islem_md(self,df):
      try:

         
        rsi_values = self.calculate_rsi(df['kapanis'], period=self.period_rsi)

        df['RSI'] = rsi_values
            
        df['en_dusuk_rsi']=df['RSI'].rolling(window=self.periot_stoph).min()
        df['en_yuksek_rsi']=df['RSI'].rolling(window=self.periot_stoph).max()
        df['stoch_RSI']=(((df['RSI']-df['en_dusuk_rsi'])/(df['en_yuksek_rsi']-df['en_dusuk_rsi']))*100)
            
        df['hesap_beyaz'] = df['stoch_RSI'].rolling(window=3).mean()

            
        df['hesap_kirmizi'] = df['hesap_beyaz'].rolling(window=3).mean()
        df.drop(columns=['RSI','en_dusuk_rsi','en_yuksek_rsi','stoch_RSI'],inplace=True)
    
        return df
      
      except Exception as e:

        mongo = hata_kaydet()
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp)
            
        hata = {
                'hata': str(e),
                'aciklama': f"si_rsi_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
        }
        mongo.insert_one(hata)
        return df  
          
          

    @staticmethod
    def calculate_rsi(close_prices, period=8):
          
      close_prices = pd.to_numeric(close_prices, errors='coerce')
      delta = close_prices.diff()

      gain = delta.where(delta > 0, 0)
      loss = -delta.where(delta < 0, 0)

      
      avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
      avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

      rs = avg_gain / avg_loss
      rsi = 100 - (100 / (1 + rs))

      return rsi

    