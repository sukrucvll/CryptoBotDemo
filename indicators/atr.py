import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import numpy as np
from storage.mongo_db import get_db,hata_kaydet
import time



class ATR:
    
    def __init__(self, name,zaman_dilimi,period):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period
          

    def atr_hesapla_yuzde(self,df):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
            for i in ['acilis','kapanis','yuksek','dusuk']:
                df[i]=pd.to_numeric(df[i],errors='coerce')
            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=14).mean()

            ATR = df['ATR'].iloc[-1]
            kapanis = df['kapanis'].iloc[-1]

            df['ATR_yuzde'] = round((ATR / kapanis) * 100,3)
          
            
            return df
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesapla fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df
    
    def atr_hesapla(self,df,period=14):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
            for i in ['acilis','kapanis','yuksek','dusuk']:
                df[i]=pd.to_numeric(df[i],errors='coerce')
            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            tr1 = df['yuksek'] - df['dusuk']
            tr2 = (df['yuksek'] - df['onceki_kapanis']).abs()
            tr3 = (df['dusuk'] - df['onceki_kapanis']).abs()

            df['gercek_aralik'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            atr = pd.Series(index=df.index, dtype='float64')
            atr.iloc[period-1] = df['gercek_aralik'].iloc[:period].mean()

            for i in range(period, len(df)):
                atr.iloc[i] = (atr.iloc[i-1] * (period - 1) + df['gercek_aralik'].iloc[i]) / period

            df['ATR'] = atr
            
            return df['ATR'].iloc[-1]
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesapla fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return 0.10
       
    def atr_hesaplama_islemi_sonrasi(self,df,anlik_deger):
        try:
            
            if df['ATR'].iloc[-1] < 0.18:
                katsayi = 1.35
            elif df['ATR'].iloc[-1] < 0.35:
                katsayi = 1.45
            else:
                katsayi = 1.65

            df['stop_loss'] = df['kapanis'] - katsayi * df['ATR']
            stoplos_degeri = df['stop_loss'].iloc[-1]

            df.drop(columns=['stop_loss'], inplace=True)
            
            return stoplos_degeri 
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islemi_sonrasi fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']

    def atr_hesaplama_islem_alt_1(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    

            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat  
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim

            if atr_oran < 0.0015:       
                katsayi = 1.5
            elif atr_oran < 0.003:     
                katsayi = 1.6
            elif atr_oran < 0.006:     
                katsayi = 1.8
            else:                   
                katsayi = 2

            if hacim_oran < 0.8:
                hacim_katsayi = 1.2     
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.3     
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.5    
            else:
                hacim_katsayi = 1.7  

            katsayi = katsayi * hacim_katsayi

            stoplos_degeri = anlik_deger - katsayi * df['ATR'].iloc[-1]
            kar_deger=((anlik_deger- stoplos_degeri)/anlik_deger)*100
                        
            
            return stoplos_degeri,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
    
    def atr_hesaplama_islem_alt_2(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat   
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim
             
            if atr_oran < 0.0015:       
                katsayi = 1.3
            elif atr_oran < 0.003:      
                katsayi = 1.5
            elif atr_oran < 0.006:      
                katsayi = 1.7
            else:                   
                katsayi = 1.9

            if hacim_oran < 0.8:
                hacim_katsayi = 1.1     
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.2    
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.4    
            else:
                hacim_katsayi = 1.6     

            katsayi = katsayi * hacim_katsayi

            stoplos_degeri = anlik_deger - katsayi * df['ATR'].iloc[-1]
            
            kar_deger=((anlik_deger- stoplos_degeri)/anlik_deger)*100
            
            if kar_deger>0.7:
                kar_deger=0.7
                stoplos_degeri=anlik_deger-(kar_deger/100)*anlik_deger            
            
            return stoplos_degeri,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
    def atr_hesaplama_islem_kar_alt_1(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat   
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim
                   


            if atr_oran < 0.0015:       
                katsayi = 1.6
            elif atr_oran < 0.003:     
                katsayi = 1.8
            elif atr_oran < 0.006:     
                katsayi = 1.95
            else:                     
                katsayi = 2.15

            if hacim_oran < 0.8:
                hacim_katsayi = 1.35    
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.55    
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.75    
            else:
                hacim_katsayi = 1.95     

            katsayi = katsayi * hacim_katsayi

            

            kar = anlik_deger + katsayi * df['ATR'].iloc[-1]
            kar_deger=((kar- anlik_deger)/anlik_deger)*100

           
            
            
            return kar,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
     
    def atr_hesaplama_islem_kar_alt_2(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    

            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat   
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim
                   


            if atr_oran < 0.0015:        
                katsayi = 1.5
            elif atr_oran < 0.003:    
                katsayi = 1.6
            elif atr_oran < 0.006:     
                katsayi = 1.75
            else:                   
                katsayi = 1.95

            if hacim_oran < 0.8:
                hacim_katsayi = 1.2     
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.3  
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.5   
            else:
                hacim_katsayi = 1.75    

            katsayi = katsayi * hacim_katsayi

            kar = anlik_deger + katsayi * df['ATR'].iloc[-1]
            kar_deger=((kar- anlik_deger)/anlik_deger)*100

           
            return kar,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
    
    def atr_hesaplama_islem_md_dusus(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    

            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat   
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim
                   


            if atr_oran < 0.0015:      
                katsayi = 1.35
            elif atr_oran < 0.003:     
                katsayi = 1.50
            elif atr_oran < 0.006:     
                katsayi = 1.70
            else:                     
                katsayi = 1.90

            if hacim_oran < 0.8:
                hacim_katsayi = 1.25     
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.3   
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.5   
            else:
                hacim_katsayi = 1.7     

            katsayi = katsayi * hacim_katsayi

       


            stoplos_degeri = anlik_deger + katsayi * df['ATR'].iloc[-1]
            kar_deger=((stoplos_degeri- anlik_deger)/anlik_deger)*100
            if kar_deger>0.7:
                kar_deger=0.7
                stoplos_degeri=anlik_deger+(kar_deger/100)*anlik_deger
            
            
            return stoplos_degeri,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
    def atr_hesaplama_islem_md_2_dusus(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    

            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat  
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim
                   


            if atr_oran < 0.0015:       
                katsayi = 1.25
            elif atr_oran < 0.003:     
                katsayi = 1.4
            elif atr_oran < 0.006:      
                katsayi = 1.6
            else:                      
                katsayi = 1.8

            if hacim_oran < 0.8:
                hacim_katsayi = 1.25      
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.3     
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.5   
            else:
                hacim_katsayi = 1.7    

            katsayi = katsayi * hacim_katsayi

            stoplos_degeri = anlik_deger + katsayi * df['ATR'].iloc[-1]
            
            
            kar_deger=((stoplos_degeri- anlik_deger)/anlik_deger)*100

            if kar_deger>0.7:
                kar_deger=0.7
                stoplos_degeri=anlik_deger+(kar_deger/100)*anlik_deger
                        
            
            return stoplos_degeri,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
    def atr_hesaplama_islem_kar_dusus(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat   
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim

            if atr_oran < 0.0015:       
                katsayi = 1.6
            elif atr_oran < 0.003:      
                katsayi = 1.75
            elif atr_oran < 0.006:      
                katsayi = 1.95
            else:                      
                katsayi = 2.05

            if hacim_oran < 0.8:
                hacim_katsayi = 1.4     
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.55     
                hacim_katsayi = 1.75    
            else:
                hacim_katsayi = 1.95    

            katsayi = katsayi * hacim_katsayi

         

            kar = anlik_deger - katsayi * df['ATR'].iloc[-1]
            

            kar_deger=abs(((anlik_deger- kar)/anlik_deger)*100)

            if kar_deger>0.85:
                kar_deger=0.85
                kar=anlik_deger-(kar_deger/100)*anlik_deger
           
            
            return kar,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']
    
    def atr_hesaplama_islem_kar_2_dusus(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=8).mean()

            atr = df['ATR'].iloc[-1]
            fiyat = df['kapanis'].iloc[-1]

            atr_oran = atr / fiyat  
            son_hacim = df['hacim'].iloc[-1]
            ortalama_hacim = df['hacim'].rolling(20).mean().iloc[-1]

            hacim_oran = son_hacim / ortalama_hacim

            if atr_oran < 0.0015:        
                katsayi = 1.4
            elif atr_oran < 0.003:      
                katsayi = 1.45
            elif atr_oran < 0.006:     
                katsayi = 1.65
            else:                       
                katsayi = 1.850

            if hacim_oran < 0.8:
                hacim_katsayi = 1.25    
            elif hacim_oran < 1.3:
                hacim_katsayi = 1.4    
            elif hacim_oran < 2.0:
                hacim_katsayi = 1.6    
            else:
                hacim_katsayi = 1.    

            katsayi = katsayi * hacim_katsayi

           
            kar = anlik_deger - katsayi * df['ATR'].iloc[-1]
            kar_deger=abs(((anlik_deger- kar)/anlik_deger)*100)

            if kar_deger>0.85:
                kar_deger=0.85
                kar=anlik_deger-(kar_deger/100)*anlik_deger
           
            
            
            return kar,kar_deger
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-1]['kapanis']


    def atr_hesaplama_islem_orta_band(self,df,anlik_deger):
        try:
     
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
           
            
            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=14).mean()

            if df['ATR'].iloc[-1] < 0.20:
                katsayi = 1.35
            elif df['ATR'].iloc[-1] < 0.35:
                katsayi = 1.55
            else:
                katsayi = 1.75

            df['stop_loss'] = df['kapanis'] - katsayi * df['ATR']

            stop_degeri = df['stop_loss'].iloc[-1]
            df.drop(columns=['stop_loss'], inplace=True)

            
            return stop_degeri 
        
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_orta_band fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-2]['kapanis']
    
    
    
    def atr_hesaplama_islem_orta_band_dusus(self,df,anlik_deger):
        try:
     
            pd.set_option('display.float_format', lambda x: '%.8f' % x)

            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralik'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralik'].rolling(window=14).mean()

            if df['ATR'].iloc[-1] < 0.20:
                katsayi = 1.3
            elif df['ATR'].iloc[-1] < 0.35:
                katsayi = 1.45
            else:
                katsayi = 1.6
            

            df['stop_loss'] = df['kapanis'] + katsayi * df['ATR']
            stop_deger= df['stop_loss'].iloc[-1]
            df.drop(columns=['stop_loss','ATR','gercek_aralik','yuksek_fark','dusuk_fark','yuksek_dusuk_fark','onceki_kapanis'], inplace=True)
            
            return stop_deger 
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_orta_band_dusus fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-2]['acilis']
        
        

    def atr_hesaplama_islem_md_yarim(self,df,anlik_deger):
        try:

            pd.set_option('display.float_format', lambda x: '%.8f' % x)

            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gerçek_aralık'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gerçek_aralık'].rolling(window=18).mean()


            if df['ATR'].iloc[-1] < 0.20:
                katsayi = 2
            elif df['ATR'].iloc[-1] < 0.35:
                katsayi = 2.85
            else:
                katsayi = 3
        
            df['stop_loss'] = df['kapanis'] - katsayi * df['ATR']
            stop_los=df.iloc[-1]['stop_loss']
            df.drop(columns=['stop_loss','ATR','gerçek_aralık','yuksek_fark','dusuk_fark','yuksek_dusuk_fark','onceki_kapanis'], inplace=True)

            return stop_los 
        
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md_yarim fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-2]['kapanis']
       
    def atr_hesaplama_islemi_yesil(self,df,anlik_deger):
        try:
            pd.set_option('display.float_format', lambda x: '%.8f' % x)

            df['onceki_acilis'] = df['acilis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_acilis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_acilis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gercek_aralık'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gercek_aralık'].rolling(window=14).mean()

           
            if df['ATR'].iloc[-1] < 0.20:
                katsayi = 1.3
            elif df['ATR'].iloc[-1] < 0.35:
                katsayi = 1.6
            else:
                katsayi = 1.9


            df['stop_loss'] = df['acilis'] - katsayi * df['ATR']
            stop_loss_degeri = df['stop_loss'].iloc[-1]
            
            df.drop(columns=['stop_loss','ATR','gercek_aralık','yuksek_fark','dusuk_fark','yuksek_dusuk_fark','onceki_acilis'], inplace=True)
            return stop_loss_degeri 
                
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islemi_yesil fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-2]['kapanis']
    
    def atr_hesaplama_islemi_kirmizi(self,df,anlik_deger):
        try:
            df1 = df.copy(deep=True).reset_index(drop=True)
            
            df1['onceki_kapanis'] = df1['kapanis'].shift(1)
            
            df1['yuksek_fark'] = abs(df1['yuksek'] - df1['onceki_kapanis'])
            df1['dusuk_fark'] = abs(df1['dusuk'] - df1['onceki_kapanis'])
            df1['yuksek_dusuk_fark'] = abs(df1['yuksek'] - df1['dusuk'])

            df1['gerçek_aralık'] = df1[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df1['ATR'] = df1['gerçek_aralık'].rolling(window=14).mean()

            if df1['ATR'].iloc[-1] < 0.20:
                katsayi = 1.1
            elif df1['ATR'].iloc[-1] < 0.35:
                katsayi = 1.3
            else:
                katsayi = 1.4
            
        
            df1['stop_loss'] = df1['kapanis'] + katsayi * df1['ATR']
            stop_deger= df1['stop_loss'].iloc[-1]
            df.drop(columns=['stop_loss','ATR','gerçek_aralık','yuksek_fark','dusuk_fark','yuksek_dusuk_fark','onceki_kapanis'], inplace=True)
            return stop_deger 
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islemi_kirmizi fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-2]['acilis']
        
    def atr_hesaplama_islem_md_yarim_dusus(self,df,anlik_deger):
        try:

            df['onceki_kapanis'] = df['kapanis'].shift(1)
            
            df['yuksek_fark'] = abs(df['yuksek'] - df['onceki_kapanis'])
            df['dusuk_fark'] = abs(df['dusuk'] - df['onceki_kapanis'])
            df['yuksek_dusuk_fark'] = abs(df['yuksek'] - df['dusuk'])

            df['gerçek_aralık'] = df[['yuksek_fark', 'dusuk_fark', 'yuksek_dusuk_fark']].max(axis=1)
            df['ATR'] = df['gerçek_aralık'].rolling(window=14).mean()

            if df['ATR'].iloc[-1] < 0.20:
                katsayi = 0.9
            elif df['ATR'].iloc[-1] < 0.35:
                katsayi = 1
            else:
                katsayi = 1.1
                
        
            df['stop_loss'] = df['kapanis'] + katsayi * df['ATR']
            stop_deger= df['stop_loss'].iloc[-1]
            df.drop(columns=['stop_loss','ATR','gerçek_aralık','yuksek_fark','dusuk_fark','yuksek_dusuk_fark','onceki_kapanis'], inplace=True)
            return stop_deger 
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"atr_hesaplama_islem_md_yarim_dusus fonkisiyonunda hesaplanirken '{self.name}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
            return df.iloc[-2]['acilis']      

