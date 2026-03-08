# utils/data_fetcher.py
import sys
import os
import asyncio
# Proje klasörünü import yoluna ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import requests
import pandas as pd
import time
import datetime
from indicators import ATR
from storage.mysql_db import baglan_alis_satis
from storage.mongo_db import hata_kaydet



def get_futures_price(symbol):
    try:
        url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol.upper()}"
        response = requests.get(url)
        data = response.json()
    
        if "price" in data:
           return float(data["price"])
        else:
            print(f"{symbol} için veri alınamadı: {data}")
            return None
    except Exception as e:

        mongo = hata_kaydet()
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp)
            
        hata = {
                'hata': str(e),
                'aciklama': f"get_futures_price fonkisiyonunda veri çekerken '{symbol}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
        mongo.insert_one(hata)

        print(f"{symbol} fiyat alınırken hata: {e}")
        return None



def get_binance_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}"
        response = requests.get(url)
        data = response.json()

        if "price" in data:
            return round(float(data["price"]), 8)
        else:
            print(f"{symbol} için veri alınamadı: {data}")
            return None

    except Exception as e:

        mongo = hata_kaydet()
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp)
            
        hata = {
                'hata': str(e),
                'aciklama': f"get_binance_price fonkisiyonunda veri çekerken  '{symbol}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
        mongo.insert_one(hata)

        print(f"{symbol} fiyat alınırken hata: {e}")
        return None



def alt_alis_islemler(coin,alinan_deger,alinan_fiyat,islem=0,kar_degeri=0,stop_deger=0):
    
    db,cursor=baglan_alis_satis()
    
   
    tablo='alt_alis_islemler'
    cursor.execute(f"SHOW TABLES LIKE %s",(tablo,))
    sonuc = cursor.fetchone()

    if not sonuc:
        cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS `{tablo}` (
                        id INT NOT NULL  AUTO_INCREMENT,
                        coin VARCHAR(45),
                        zaman VARCHAR(45),
                        alis FLOAT,  
                        kar_degeri FLOAT,  
                        stop_deger FLOAT,  
                        islem INT,

                        PRIMARY KEY(id))
                                                
                        """)
        
        db.commit()

    sqll=f"Insert Into `{tablo}` (coin,zaman,alis,kar_degeri,stop_deger,islem) Values(%s,%s,%s,%s,%s,%s)"
    values=(coin, alinan_deger,alinan_fiyat,kar_degeri,stop_deger,islem)

    try:
            
        cursor.execute(sqll,values)
        db.commit()
    except Exception as e:
        mongo = hata_kaydet()
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp)
            
        hata = {
                'hata': str(e),
                'aciklama': f"alt_alis_islemler sql de yazarken  '{coin}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
        }
        mongo.insert_one(hata)
    finally:       
        db.close()



def alt_satis_islemler(coin,alinan_deger_zaman,alinan_fiyat,pozisyon_sayisi,islem=0):
    db,cursor=baglan_alis_satis()


    tablo='alt_satis_islemler'
    cursor.execute(f"SHOW TABLES LIKE %s",(tablo,))
    sonuc = cursor.fetchone()
        
    if not sonuc:
        cursor.execute(f"""
                        CREATE TABLE IF NOT EXISTS `{tablo}` (
                        id INT NOT NULL  AUTO_INCREMENT,
                        coin VARCHAR(45),
                        zaman VARCHAR(45),
                        satis FLOAT,
                        pozisyon_sayisi INT ,
                        islem INT,
                        
                        PRIMARY KEY(id))
                                                
                        """)
        
        db.commit()

    sqll=f"Insert Into `{tablo}` (coin,zaman,satis,pozisyon_sayisi,islem) Values(%s,%s,%s,%s,%s)"
    values=(coin, alinan_deger_zaman,alinan_fiyat,pozisyon_sayisi,islem)
        

    try:
            
        cursor.execute(sqll,values)
        db.commit()
    except Exception as e:
        mongo = hata_kaydet()
        timestamp = time.time()
        dt = datetime.datetime.fromtimestamp(timestamp)
            
        hata = {
                'hata': str(e),
                'aciklama': f"alt_satis_islemler sql de yazarken  '{coin}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
        }
        mongo.insert_one(hata)
    finally:
        db.close()


def karar_yukselis_alis(coin,dff,alis_pozisyon,sayi,stop_deger,alinan_fiyat=0,orta_band_ustu=False,alinandan_son_stop=0,islem=0,kar_degeri=0):
    
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
    dff = dff.copy()

    
    alinan_deger=dff.iloc[-1]
   

    if alis_pozisyon==0:

        alinan_fiyat=(alinan_deger['kapanis']+alinan_deger['acilis'])/2
        bb_ust = alinan_deger['ust_band']
        bb_alt = alinan_deger['alt_band']
        yuzde_fark = ((bb_ust - bb_alt) / bb_alt) * 100

        orta_band_uzaklik= abs(alinan_deger['orta_band'] - alinan_fiyat)/alinan_fiyat *100
        alt_band_uzaklik= abs(alinan_deger['alt_band'] - alinan_fiyat)/alinan_fiyat *100
        if alt_band_uzaklik>0.4:
           stop1= alt_band_uzaklik*0.8
           kar=alt_band_uzaklik*1.2
        elif alinan_deger['alt_band']>alinan_fiyat:
             stop1= alinan_fiyat* 0.997
             kar=  alinan_fiyat *1.006
        else:
            if orta_band_uzaklik>0.6:
                stop1= yuzde_fark*0.4
                kar= yuzde_fark*0.7
            else:
                stop1=yuzde_fark*0.3
                kar=yuzde_fark*0.6
        

        kar_degeri= alinan_fiyat + (alinan_fiyat * kar / 100)
        stop_deger=alinan_fiyat - (alinan_fiyat * stop1 / 100)


        stop2 = stop_deger
        alt_alis_islemler(coin,alinan_deger['zaman_damgasi'],alinan_fiyat,islem,kar_degeri,stop_deger)

        return 1,0,stop_deger,alinan_fiyat,orta_band_ustu,stop2,kar_degeri

    else:
        
        anlik_fiyat=(alinan_deger['kapanis']+alinan_deger['acilis'])/2
        
        anlik_fiyat_2=(alinan_deger['acilis'])
        anlik_fiyat_3=(alinan_deger['kapanis'])

        sayi+=1
    
        if alinan_deger['ust_banda_yaklasti_satis'] :
            
                
            alt_satis_islemler(coin,alinan_deger['zaman_damgasi'],anlik_fiyat,sayi,islem)
            return 0,sayi,stop_deger,alinan_fiyat,orta_band_ustu,alinandan_son_stop,kar_degeri
        
        
        if  anlik_fiyat >= kar_degeri or anlik_fiyat_2 >= kar_degeri or anlik_fiyat_3 >= kar_degeri:
               
                alt_satis_islemler(coin,alinan_deger['zaman_damgasi'],kar_degeri,sayi,islem)
                return 0,sayi,stop_deger,alinan_fiyat,orta_band_ustu,alinandan_son_stop,kar_degeri
        
        elif stop_deger >= anlik_fiyat or stop_deger >= anlik_fiyat_2 or stop_deger >= anlik_fiyat_3 :

                alt_satis_islemler(coin,alinan_deger['zaman_damgasi'],stop_deger,sayi,islem)
               
                return  0,sayi,stop_deger,alinan_fiyat,orta_band_ustu,alinandan_son_stop,kar_degeri
        else:
                return  1,sayi,stop_deger,alinan_fiyat,orta_band_ustu,alinandan_son_stop,kar_degeri