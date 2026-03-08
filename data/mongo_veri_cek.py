
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import datetime
import pandas as pd
import requests
import numpy as np
from binance.client import Client
from api.binance_ import bagla
# from storage.mongo_db  import mycollection
from storage.mongo_db import get_db,delete_database
# import storage.mongo_db
from datetime import datetime, timedelta
import time
from ulitis.coin_isim  import zaman_dilimi
mydb = get_db('coin_listesi')
mycollection= mydb['coin_isimleri']
coin_liste_mongo=mycollection.find({},{'coin':1, "_id": 0})
coin_listesi=list(coin_liste_mongo)
coin_listesi={coin['coin']  for coin in coin_listesi}

coin_listesi=['SOLUSDT']
class VeriCek:

    
    def __init__(self, name,zaman_dilimi,start_date):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.start_date=start_date

    def zaman_degeri(self):
        
        start_date = (datetime.now() - timedelta(days=self.start_date)).strftime("%d %b %Y %H:%M:%S")
        return start_date


    def veri_cek(self):

        try:
            start_date = self.zaman_degeri()
            print(start_date)
        
          
            veri = bagla.get_historical_klines(self.name, self.zaman_dilimi, start_str=start_date)


        

            columns = ['zaman_damgasi', 'acilis', 'yuksek', 'dusuk', 'kapanis', 'hacim', 
                'kapanis_zamani', 'teklif varlik_hacmi', 'islem_sayisi', 
                'alici_baz_hacmi', 'aliciteklif_hacmi', 'bakma']

            
            df=pd.DataFrame(veri,columns=columns)
            df.drop(columns=['bakma','teklif varlik_hacmi', 'islem_sayisi', 
                'alici_baz_hacmi', 'aliciteklif_hacmi'], inplace=True)


            df['zaman_damgasi'] = pd.to_datetime(df['zaman_damgasi'], unit='ms') + timedelta(hours=3)
            df['kapanis_zamani'] = pd.to_datetime(df['kapanis_zamani'], unit='ms') + timedelta(hours=3)
            df['zaman_damgasi'] = df['zaman_damgasi'].dt.strftime('%Y-%m-%d %H:%M')
            df['kapanis_zamani'] = df['kapanis_zamani'].dt.strftime('%Y-%m-%d %H:%M')

        

            veriler = df.to_dict(orient="records")  
        
            mydb = get_db(self.name) 
            
            koleksiyon_adi = self.name + "_" + self.zaman_dilimi + "_veri"
            mycollection = mydb[koleksiyon_adi]
        except Exception as e:
            print(e)

        try:
            mycollection.insert_many(veriler)
        except Exception as e:
            print(f"{self.name} verisi MongoDB'ye kaydedilemedi: {e}")

        
        
def fetch_coin_data(coin,zaman_dilimi,start_date):
  
  veri_nesnesi = VeriCek(coin, zaman_dilimi, start_date)

  veri_nesnesi.veri_cek()

zaman_dilimi = ['5m']


start=time.time()
for coin in coin_listesi:
    for zaman in zaman_dilimi:
        fetch_coin_data(coin,zaman,1)
        print(coin, '  için veri çekildi')

end=time.time()
print(end-start)
exit()

# mongo clear
for  coin in coin_listesi:
     for zaman in zaman_dilimi:
        mydb = get_db(coin)

        try:
            name=coin+'_'+zaman+'_veri_3' 
            
            myol=mydb[name]
        
            myol.drop()
        except Exception as e:
            print(e)
    
exit()


