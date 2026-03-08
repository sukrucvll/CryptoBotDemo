import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from binance.client import Client
from storage.mongo_db import get_db,hata_kaydet
import datetime
import time


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return False
class HAYKIN:
    
    def __init__(self, name,zaman_dilimi):
        self.name=name
        self.zaman_dilimi=zaman_dilimi

    def haykin_hesaplama_islem_md(self,df):
        
        try:
          
            df['ha_kapanis'] = (df['acilis'] + df['kapanis'] + df['yuksek'] + df['dusuk']) / 4

            ha_open = [df['acilis'].iloc[0]]
            for i in range(1, len(df)):
                ha_open.append((ha_open[i - 1] + df['ha_kapanis'].iloc[i - 1]) / 2)
            df['ha_acilis'] = ha_open

            df['ha_yuksek'] = df[['yuksek', 'ha_acilis', 'ha_kapanis']].max(axis=1)
            df['ha_dusuk']  = df[['dusuk', 'ha_acilis', 'ha_kapanis']].min(axis=1)

            current_open  = df['acilis'].iloc[-1]
            current_high  = df['yuksek'].iloc[-1]
            current_low   = df['dusuk'].iloc[-1]
            current_price = df['kapanis'].iloc[-1] 

            last_ha_close = (current_open + current_high + current_low + current_price) / 4

            if len(df) < 2:
                last_ha_open = df['acilis'].iloc[0]
            else:
                last_ha_open = (df['ha_acilis'].iloc[-2] + df['ha_kapanis'].iloc[-2]) / 2

            last_ha_high = max(current_high, last_ha_open, last_ha_close)
            last_ha_low  = min(current_low, last_ha_open, last_ha_close)


            df.at[df.index[-1], 'ha_kapanis'] = last_ha_close
            df.at[df.index[-1], 'ha_acilis']  = last_ha_open
            df.at[df.index[-1], 'ha_yuksek']  = last_ha_high
            df.at[df.index[-1], 'ha_dusuk']   = last_ha_low

            df['yesil_heiken']   = df['ha_kapanis'] > df['ha_acilis']
            df['kirmizi_heiken'] = df['ha_kapanis'] < df['ha_acilis']

            return df

        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"haykin_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df

   