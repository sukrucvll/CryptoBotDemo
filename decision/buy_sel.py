import sys
import os
import pandas as pd
import asyncio
import json
from datetime import datetime, timedelta,timezone
import numpy as np
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
if sys.platform.startswith('win') and sys.version_info >= (3, 8):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
import keyboard

import time
from ulitis.data_fetcher import get_all_klines_async
from ulitis.coin_isim  import zaman_dilimi ,coin_listesi

from decision.decisions import karar_alt 
from indicators import RSI,MFI,BB,WILR,STRSI,DMI,ATR,MACD,HAYKIN,TRIX,CCI

from storage.mongo_db import get_db,hata_kaydet
from mum.mum_yukselis import mum_teyit_alt

from streaming.decription_time_fetcher import karar_yukselis_alis


coin_statelari_alt = {coin: {"tutan_islem": 0, "sayac": 0,"islem":0 } for coin in coin_listesi}
coin_bb_onay_alt = {coin: {"tutan_islem": 0,  "sayac": 0 } for coin in coin_listesi}
coin_statelari_ust = {coin: {"tutan_islem": 0,  "sayac": 0,'islem':0 } for coin in coin_listesi}
coin_alt_alis_pozisyon={coin:{'pozisyon':0,'sayi':0,'stop' : 0,'ilk_fiyat':0,'orta_band':False,'alinan_son_stop':0,'kar_degeri':0} for coin in coin_listesi}

pd.set_option('display.max_columns', None)

def lower_band_transactions(coin, df, coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon):
        
    if coin_alt_alis_pozisyon[coin]['pozisyon']==0:
            
        if coin_bb_onay_alt[coin]['tutan_islem'] != 1:
            print(f"{coin} - İlk defa teyit 1 geldi, zaman kaydediliyor.")
            coin_bb_onay_alt[coin]['sayac'] = 1
           
            
        else:
            print(f"{coin} - Daha önce teyit 1 almış, işlem tekrar kontrol ediliyor.")

        coin_bb_onay_alt[coin]['tutan_islem'] = 1
        coin_bb_onay_alt[coin]['sayac'] += 1
        karar_3_dk=1


        if coin_statelari_alt[coin]['tutan_islem']!=1:
            
           
            coin_statelari_alt[coin]['tutan_islem'],coin_statelari_alt[coin]['islem'] = karar_alt(df, coin_statelari_alt[coin]['tutan_islem'],karar_3_dk)
         
        else:
            mum_onay, df = mum_teyit_alt(coin, df)
            
 
            if mum_onay:    
                coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_alt_alis_pozisyon[coin]['kar_degeri'] = karar_yukselis_alis(coin,df,coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_statelari_alt[coin]['islem'],coin_alt_alis_pozisyon[coin]['kar_degeri'])

                coin_bb_onay_alt[coin]['tutan_islem']=0
 
                coin_bb_onay_alt[coin]['tutan_islem']=0
                coin_bb_onay_alt[coin]['sayac']=0
         
                coin_statelari_alt[coin]['tutan_islem']=0
                coin_statelari_alt[coin]['sayac']=0
               
                return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon
            else:
                coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_alt_alis_pozisyon[coin]['kar_degeri'] = karar_yukselis_alis(coin,df,coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_statelari_alt[coin]['islem'],coin_alt_alis_pozisyon[coin]['kar_degeri'])

                coin_bb_onay_alt[coin]['tutan_islem']=0
 
                coin_bb_onay_alt[coin]['tutan_islem']=0
                coin_bb_onay_alt[coin]['sayac']=0
               
                coin_statelari_alt[coin]['tutan_islem']=0
                coin_statelari_alt[coin]['sayac']=0
                
                return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon

        if coin_statelari_alt[coin]['tutan_islem'] in [0, None]:
            
         
            if(coin_statelari_alt[coin]['tutan_islem']==4):

                if coin_statelari_ust[coin]['tutan_islem']==1:
                    coin_statelari_ust[coin]['tutan_islem']=0
                
                
                coin_statelari_alt[coin]['tutan_islem'],coin_statelari_alt[coin]['islem'] = karar_alt(df, coin_statelari_alt[coin]['tutan_islem'],karar_3_dk)
                return df,coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon
  
            
            if(coin_statelari_alt[coin]['tutan_islem']==0):
                
                
                return df,coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon
            
        elif coin_statelari_alt[coin]['tutan_islem']==4:
            
            coin_statelari_alt[coin]['tutan_islem'],coin_statelari_alt[coin]['islem'] = karar_alt(df, coin_statelari_alt[coin]['tutan_islem'],karar_3_dk)

            print(coin_statelari_alt[coin]['tutan_islem'])
           
            return df,coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon

            
            
        elif coin_statelari_alt[coin]['tutan_islem'] == 3:
           
           
            coin_statelari_alt[coin]['tutan_islem'],coin_statelari_alt[coin]['islem'] = karar_alt(df, coin_statelari_alt[coin]['tutan_islem'],karar_3_dk)

            return df,coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon
        
        elif coin_statelari_alt[coin]['tutan_islem'] == 6:
           
            coin_statelari_alt[coin]['tutan_islem'],coin_statelari_alt[coin]['islem'] = karar_alt(df, coin_statelari_alt[coin]['tutan_islem'],karar_3_dk)

            return df,coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon
        
        elif coin_statelari_alt[coin]['tutan_islem']==1:

            mum_onay, df = mum_teyit_alt(coin, df)
            df.loc[df.index[-1],'class']=6 
          
           
            if mum_onay:  
                
                coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_alt_alis_pozisyon[coin]['kar_degeri'] = karar_yukselis_alis(coin,df,coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_statelari_alt[coin]['islem'],coin_alt_alis_pozisyon[coin]['kar_degeri'])

                coin_bb_onay_alt[coin]['tutan_islem']=0
 
                coin_bb_onay_alt[coin]['tutan_islem']=0
                coin_bb_onay_alt[coin]['sayac']=0

                coin_statelari_alt[coin]['tutan_islem']=0
                coin_statelari_alt[coin]['sayac']=0
               
                return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon
            else:
                coin_bb_onay_alt[coin]['tutan_islem']=1
 
                coin_bb_onay_alt[coin]['tutan_islem']=1
                coin_bb_onay_alt[coin]['sayac']=1

                coin_statelari_alt[coin]['tutan_islem']=3
                coin_statelari_alt[coin]['sayac']=1
                return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon


        elif coin_statelari_alt[coin]['tutan_islem']==5:

            coin_statelari_alt[coin]['tutan_islem'],coin_statelari_alt[coin]['islem'] = karar_alt(df, coin_statelari_alt[coin]['tutan_islem'],karar_3_dk)
        
            return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon
        
        return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon
    else:
      
        coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_alt_alis_pozisyon[coin]['kar_degeri']  = karar_yukselis_alis(coin,df,coin_alt_alis_pozisyon[coin]['pozisyon'],coin_alt_alis_pozisyon[coin]['sayi'],coin_alt_alis_pozisyon[coin]['stop'],coin_alt_alis_pozisyon[coin]['ilk_fiyat'],coin_alt_alis_pozisyon[coin]['orta_band'],coin_alt_alis_pozisyon[coin]['alinan_son_stop'],coin_statelari_alt[coin]['islem'],coin_alt_alis_pozisyon[coin]['kar_degeri'])
        
        if not coin_alt_alis_pozisyon[coin]['pozisyon']:
            
            if coin_alt_alis_pozisyon[coin]['sayi']<10 and coin_alt_alis_pozisyon[coin]['sayi'] >2:

                coin_bb_onay_alt[coin]['tutan_islem']=1
                coin_bb_onay_alt[coin]['sayac']=0
                coin_statelari_alt[coin]['tutan_islem']=7
                coin_statelari_alt[coin]['sayac']=0
                
                coin_alt_alis_pozisyon[coin]['orta_band']

            else:

                coin_bb_onay_alt[coin]['tutan_islem']=0
                coin_bb_onay_alt[coin]['sayac']=0
                coin_alt_alis_pozisyon[coin]['sayi']=0
                coin_alt_alis_pozisyon[coin]['alinan_son_stop']=0
                coin_alt_alis_pozisyon[coin]['ilk_fiyat']=0
                coin_alt_alis_pozisyon[coin]['stop']=0
                coin_alt_alis_pozisyon[coin]['orta_band']
                coin_statelari_alt[coin]['tutan_islem']=0
                coin_statelari_alt[coin]['sayac']=0          
       
        return df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon


async def main_loop():

    global coin_statelari_ust,  coin_statelari_alt, coin_bb_onay_alt,karar_3_dk,coin_alt_alis_pozisyon
    karar_3_dk= None
   

    while True:
      
        coin_df_dict = await get_all_klines_async(coin_listesi) 
       
        
        for coin in coin_listesi:
            
            
            for zaman in zaman_dilimi:

                start=time.time()


                db_tablo =  coin+'_'+zaman+'_veri'
                mydb = get_db(coin)
                al_veri = mydb[db_tablo]
                    
                veriler = al_veri.find({}, {
                            "zaman_damgasi": 1, "acilis": 1, "yuksek": 1, "dusuk": 1,
                            "kapanis": 1, "hacim": 1, "kapanis_zamani": 1, "_id": 0
                        })
                veri=list(veriler)

                df = pd.DataFrame(veri[:100])             
                                     

                for deger in veri[100:]:
 
                        
                    df = pd.concat([df, pd.DataFrame([deger])], ignore_index=True)

                      
                    pd.set_option('display.float_format', lambda x: '%.8f' % x)

                    df['kapanis'] = pd.to_numeric(df['kapanis'], errors='coerce')
                    df['acilis'] = pd.to_numeric(df['acilis'], errors='coerce')
                    df['yuksek'] = pd.to_numeric(df['yuksek'], errors='coerce')
                    df['dusuk'] = pd.to_numeric(df['dusuk'], errors='coerce')
                    df['hacim'] = pd.to_numeric(df['hacim'], errors='coerce')
                    df.loc[df.index[-1],'class']=0
                     

                    veri_nesnesi = HAYKIN(coin, zaman_dilimi[0])
                    df = veri_nesnesi.haykin_hesaplama_islem_md(df)
                      

                    veri_nesnesi_wilsR = WILR(coin, zaman_dilimi[0], 14)
                    df = veri_nesnesi_wilsR.wil_r_hesaplama_islem_md(df)
                        

                    veri_nesnesi_wilsR = CCI(coin, zaman_dilimi[0], 25)
                    df = veri_nesnesi_wilsR.cci_hesaplama_islem_md(df)
                        

                    veri_nesnesi = STRSI(coin, zaman_dilimi[0], 8, 10)
                    df = veri_nesnesi.si_rsi_hesaplama_islem_md(df)


                    veri_nesnesi = MFI(coin, zaman_dilimi[0], 8)
                    df = veri_nesnesi.mfi_hesaplama_islem_md(df)


                    veri_nesnesi = RSI(coin, zaman_dilimi[0], 9)
                    df = veri_nesnesi.rsi_hesaplama_islem_md(df)


                    veri_nesnesi = DMI(coin, zaman_dilimi[0], 14)
                    df = veri_nesnesi.dmi_hesaplama_islem_md(df)


                    veri_nesnesi = ATR(coin, zaman_dilimi[0], 14)
                    df = veri_nesnesi.atr_hesapla_yuzde(df)


                    veri_nesnesi = MACD(coin, zaman_dilimi[0], 12, 26)
                    df = veri_nesnesi.macd_hesaplama_islem_md(df)


                    veri_nesnesi = TRIX(coin, zaman_dilimi[0], 18)
                    df = veri_nesnesi.trix_hesaplama_islem_md(df)

                   
                    veri_nesnesi_BB = BB(coin, zaman_dilimi[0], 34, 2, 0.7)

                    yaklasma_alt , yaklasma_ust , df = veri_nesnesi_BB.bb_yaklasti_mi_test(df)

                    veri_nesnesi_BB = BB(coin, zaman_dilimi[0], 34, 2, 0.7)

                    teyit,ust_band,yaklasma_orta_yukselis, yaklasma_orta_dusus, df = veri_nesnesi_BB.bb_hesaplama_islem(df)
                        
                    if ((teyit  or coin_bb_onay_alt[coin]['tutan_islem']) or coin_alt_alis_pozisyon[coin]['pozisyon']):

                        df,coin_statelari_alt,coin_bb_onay_alt,coin_alt_alis_pozisyon = lower_band_transactions(coin, df, coin_statelari_alt, coin_bb_onay_alt,coin_alt_alis_pozisyon)
                            

                mydb = get_db(coin)
                    
                koleksiyon_adi = coin+"_"+zaman+"islemler"
                    

                veriler = df.to_dict(orient="records")
                mycollection = mydb[koleksiyon_adi]

                try:
                    mycollection.insert_many(veriler)
                        
                        
                except Exception as e:

                    mongo = hata_kaydet()
                                       
                    hata = {
                        'hata': str(e),
                        'aciklama': f"atr_hesapla fonkisiyonunda hesaplanirken '{coin}' icin hata olustu.",
                       
                    }
                    mongo.insert_one(hata)
                    print(f"{coin} verisi MongoDB'ye kaydedilemedi: {e}")

        exit()                
                                
        

