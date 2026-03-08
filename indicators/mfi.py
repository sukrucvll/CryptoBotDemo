import sys
import os

# Proje klasörünü import yoluna ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import requests
import numpy as np
from binance.client import Client
from storage.mongo_db import get_db,hata_kaydet
import time

class MFI:
    
    def __init__(self, name,zaman_dilimi,period):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period

    def mfi_hesaplama_islem_md(self,df):
        try:
                
            df['tipik_fiyat']=((df['kapanis']+df['yuksek']+df['dusuk'])/3)
            df['para_akis']=(df['tipik_fiyat'] * df['hacim'])
            
            df['pozitif_para_akis']=(df['para_akis'].where(df['tipik_fiyat']>df['tipik_fiyat'].shift(1),0))
            df['negatif_para_akis']=(df['para_akis'].where(df['tipik_fiyat']<df['tipik_fiyat'].shift(1),0))

            df['pozitif_para_akis_toplam']=(df['pozitif_para_akis'].rolling(window=int(self.period)).sum())
            df['negatif_para_akis_toplam']=(df['negatif_para_akis'].rolling(window=int(self.period)).sum())
            
            df['para_akis_orani'] = df['pozitif_para_akis_toplam'] / df['negatif_para_akis_toplam'].replace(0, 0.0001)

            df['mfi_oran']=100- (100 / (1 + df['para_akis_orani']))
            df.drop(columns=['tipik_fiyat','para_akis','para_akis_orani','pozitif_para_akis','negatif_para_akis','pozitif_para_akis_toplam','negatif_para_akis_toplam'],inplace=True)
        
            return df
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"mfi_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df
    
