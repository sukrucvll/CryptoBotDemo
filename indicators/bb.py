import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import numpy as np
from binance.client import Client
from  api.binance_ import bagla
from storage.mongo_db import get_db,hata_kaydet
import datetime
import time


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return False
class BB:
    
    def __init__(self, name,zaman_dilimi,period,std_dev,oran):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period
        self.std_dev = std_dev
        self.oran = oran
        

    def bb_hesaplama_islem(self,df):
         
        try:
            df['ortalama'] = df['kapanis'].rolling(window=self.period).mean()
            df['standar_sapma'] = df['kapanis'].rolling(window=self.period).std()
            df['ust_band'] = df['ortalama'] + (self.std_dev * df['standar_sapma'])
            df['alt_band'] = df['ortalama'] - (self.std_dev * df['standar_sapma'])
            df['band_genisligi_yuzde']=((df['ust_band']-df['alt_band'])/df['ortalama'])/100
            df['band_genisligi_yuzde_ortalama']=df['band_genisligi_yuzde'].rolling(window=20).mean()
            
            df['band_genisligi'] = df['ust_band'] - df['alt_band']
            df['band_genisligi_yuzde_oran']=((df['band_genisligi_yuzde']*100)/df['band_genisligi_yuzde_ortalama'])
            df['alt_banda_degdi'] = df['kapanis'] <= df['alt_band']
            df['ust_banda_degdi'] = df['kapanis'] >= df['ust_band']
            df['orta_band']=(df['ust_band']+df['alt_band'])/2


            df.drop(columns=['standar_sapma','ortalama','band_genisligi_yuzde_ortalama','band_genisligi_yuzde'],inplace=True)
           
            yaklasma_orani = 1/10
          

            df['alt_banda_yaklasti_10'] = (
                df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * yaklasma_orani)
            )
            
            df['ust_banda_yaklasti_10'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani)
            )

            df['alt_banda_yaklasti_20'] = (
                df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * 1/5)
            )
            
            df['ust_banda_yaklasti_20'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * 1/5)
            )

            
          
            df['alt_banda_degdi'] = (
               df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * 3/100)
            )
           
            latest_row_alt = df.iloc[-1]['alt_banda_yaklasti']
            latest_row_ust = df.iloc[-1]['ust_banda_yaklasti']
            latest_row_orta_yukselis = df.iloc[-1]['ust_banda_yaklasti']
            latest_row_orta_dusus = df.iloc[-1]['alt_banda_yaklasti']

         
            if (not latest_row_alt or pd.isna(latest_row_alt)) and (not latest_row_ust or pd.isna(latest_row_ust)) and (not latest_row_orta_yukselis or pd.isna(latest_row_orta_yukselis)) and (not latest_row_orta_dusus or pd.isna(latest_row_orta_dusus)):
                return False, False,False,False, df
            
            return safe_int(latest_row_alt),safe_int(latest_row_ust),safe_int(latest_row_orta_yukselis),safe_int(latest_row_orta_dusus), df
        except Exception as e:
            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"bb_hesaplama_islem fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return False,False,False,False, df 

    def bb_yaklasti_mi(self):
        try:
            db_tablo = self.name + '_' + self.zaman_dilimi + '_veri'
            mydb = get_db(self.name)
            al_veri = mydb[db_tablo]

            veriler = al_veri.find({}, {
                "zaman_damgasi": 1, "acilis": 1, "yuksek": 1, "dusuk": 1,
                "kapanis": 1, "hacim": 1, "kapanis_zamani": 1, "_id": 0
            })

            df = pd.DataFrame(list(veriler))  

            pd.set_option('display.float_format', lambda x: '%.8f' % x)

            df['kapanis'] = pd.to_numeric(df['kapanis'], errors='coerce')
            df['acilis'] = pd.to_numeric(df['acilis'], errors='coerce')
            df['yuksek'] = pd.to_numeric(df['yuksek'], errors='coerce')
            df['dusuk'] = pd.to_numeric(df['dusuk'], errors='coerce')
            df['hacim'] = pd.to_numeric(df['hacim'], errors='coerce')

            df['ortalama'] = df['kapanis'].rolling(window=self.period).mean()
            df['standar_sapma'] = df['kapanis'].rolling(window=self.period).std()
            df['ust_band'] = df['ortalama'] + (self.std_dev * df['standar_sapma'])
            df['alt_band'] = df['ortalama'] - (self.std_dev * df['standar_sapma'])

            df['band_genisligi'] = df['ust_band'] - df['alt_band']
            yaklasma_orani = 30/100
            yaklasma_orani_satis = 20/100
            yaklasma_orani_decision=4/10
            

            df['alt_banda_yaklasti'] = (
                df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * yaklasma_orani)
            )
            df['alt_banda_yaklasti_decision'] = (
                df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * yaklasma_orani_decision)
            )
            
            
            df['ust_banda_yaklasti'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani)
            )
            df['ust_banda_yaklasti_decision'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani_decision)
            )
            df['ust_banda_yaklasti_satis'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani_satis)
            )
          
            
            df.drop(columns=['standar_sapma', 'ortalama', 'alt_band', 'ust_band'], inplace=True)
           
            yaklasma_alt = bool(df.iloc[-1]['alt_banda_yaklasti'])
            yaklasma_ust = bool(df.iloc[-1]['ust_banda_yaklasti'])



            return yaklasma_alt,yaklasma_ust, df

        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"bb_yaklasti_mi fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return False, False,pd.DataFrame() 

    def bb_yaklasti_mi_test(self,df):
        try:
         
            df['ortalama'] = df['kapanis'].rolling(window=self.period).mean()
            df['standar_sapma'] = df['kapanis'].rolling(window=self.period).std()
            df['ust_band'] = df['ortalama'] + (self.std_dev * df['standar_sapma'])
            df['alt_band'] = df['ortalama'] - (self.std_dev * df['standar_sapma'])

            df['band_genisligi'] = df['ust_band'] - df['alt_band']
            yaklasma_orani = 30/100
            yaklasma_orani_satis = 20/100
            yaklasma_orani_decision = 4/10

            df['alt_banda_yaklasti'] = (
                df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * yaklasma_orani)
            )
            df['alt_banda_yaklasti_decision'] = (
                df['kapanis'] <= df['alt_band'] + (df['band_genisligi'] * yaklasma_orani_decision)
            )
            
            df['ust_banda_yaklasti'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani)
            )
            df['ust_banda_yaklasti_decision'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani_decision)
            )
            df['ust_banda_yaklasti_satis'] = (
                df['kapanis'] >= df['ust_band'] - (df['band_genisligi'] * yaklasma_orani_satis)
            )


            df.drop(columns=['standar_sapma', 'ortalama', 'alt_band', 'ust_band'], inplace=True)
           
            yaklasma_alt = bool(df.iloc[-1]['alt_banda_yaklasti'])
            yaklasma_ust = bool(df.iloc[-1]['ust_banda_yaklasti'])


            return yaklasma_alt,yaklasma_ust, df

        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"bb_yaklasti_mi_test fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return False, False,pd.DataFrame()

    