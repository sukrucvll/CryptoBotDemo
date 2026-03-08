
import numpy  as np
import pandas as pd
from storage.mongo_db import get_db,hata_kaydet
import time
import datetime

def karar_alt(df, tutan_islem,karar_3_dk):
        row = df.iloc[-1]

       
        row_son3_df = df.iloc[-3:]
        row_son4_df = df.iloc[-4:]
        row_son8_df = df.iloc[-8:]
        row_son12_df = df.iloc[-12:]
        row_son6_df = df.iloc[-6:]
        row_son70_df = df.iloc[-70:]
        
        row_son2_deger = df.iloc[-2:]
        row_son2_tek=df.iloc[-2:-1]
# sample buy sell rules

        if tutan_islem == 0 :

            if not row['alt_banda_yaklasti_decision']:
                return  0,10
 
            
            katilar = [
                (row_son3_df['wil_r'] < -85).any(),
                (row_son3_df['hesap_beyaz'] <= 4).any(),
                (row_son3_df['hesap_kirmizi'] <= 8).any(),
              
                (row_son3_df['RSI'] < 30).any(),
                (row_son3_df['mfi_oran'] < 28).any(),
                row['ADX'] < 35,
                row['band_genisligi_yuzde_oran'] < 380,                
            ]
          
            esnekler = [
                
                (row_son3_df['wil_r'] < -82).any(),
                (row_son3_df['hesap_beyaz'] <= 5).any(),
                (row_son3_df['hesap_kirmizi'] <= 10).any(),
               
                (row_son3_df['RSI'] < 33).any(),
                (row_son3_df['mfi_oran'] < 32).any(),
                row['ADX'] < 38,
                row['band_genisligi_yuzde_oran'] < 410,                
               

                ]
        
            bb_ust = row['ust_band']
            bb_alt = row['alt_band']
            yuzde_fark = ((bb_ust - bb_alt) / bb_alt) * 100
            onay_1= 2.8>yuzde_fark>0.9

            onay_2=(row_son4_df['DX']>35).any()
                
               
            di_14 = df['+DI14'].tail(3).tolist()
            di_14_ = df['-DI14'].tail(3).tolist()
            onay_4 = len(di_14) == 3 and (di_14_[2]-di_14[2] <=di_14_[1]-di_14[1]   <= di_14_[0]-di_14[0])
            dx = df['DX'].tail(6).tolist()
            onay_5=dx[5]==dx[4] or dx[4]==dx[3] or dx[3]==dx[2] or dx[2]==dx[1] or dx[1]==dx[0] and dx[5]<=dx[4]
            if not onay_5:
                if row['DX']<=35 or dx[3]-25 > dx[5]:
                    onay_5=True
            
            onay_6=(round(dx[5],5)==round(dx[4],5) or round(dx[4],5)==round(dx[3],5))
           
            onay_9=di_14[1] -1.5 <= di_14[2]
            
            onay_10=row_son2_tek['DX'].iloc[0] >row['DX']
            
            onay_12=row['kapanis']>row['acilis']
                
            onay_13=row['-DI14'] -7 >= row['+DI14']
            onay_14=row['-DI14'] - row['+DI14']<=30
            onay_15=row['hesap_beyaz']<=45
            onay_16=(row_son12_df['hesap_beyaz']>=85).any()
            cci = df['CCI'].tail(3).tolist()
            onay_17=cci[1]>=cci[0]+6 and cci[2]>=cci[1]+6
            onay_18=row['CCI']>-100
            onay_19=row['kapanis']>row['acilis']

            false_indexes = [i for i, condition in enumerate(katilar) if not condition]

            if len(false_indexes) == 0:
    
                return  4,10  

            elif len(false_indexes) <=4 :
                
                esnek_uyumsuzluk = sum([not esnekler[i] for i in false_indexes])
                if esnek_uyumsuzluk <= 1:
                                       
                    return  4,10  
                else:
                    if  onay_2 and onay_5  and onay_4 and onay_18 and onay_9 and onay_10 and onay_17 and   onay_12 and onay_13 and onay_14 and onay_1 :
                    
                        return 1,7
                    if    onay_6 and onay_1 and onay_15 and onay_16 and onay_17 and onay_19:
                        
                        return 1,20
                                  
            else:
               
              
                if  onay_2 and onay_5 and  onay_4 and onay_18 and onay_9 and onay_10 and onay_17  and onay_12 and onay_13 and onay_14 and onay_1:
                    
                    return 1,7
                
                if  onay_6 and onay_1 and onay_15 and onay_16 and onay_17 and onay_19:
                    
                    return 1,20
                
            return  0,10 
        
        else:
          
            if (row_son2_deger['kapanis'] > row_son2_deger['orta_band']).all():
                return 0,10
            
       
            if tutan_islem != 5:
                if row_son70_df['ust_banda_yaklasti_10'].sum()<=3:
                    return 0,10

                
                if tutan_islem==7:
                   
                   
                    if row['trix_dusus']==False:
                        return 0,10
                    if row['ust_banda_yaklasti']==True:
                        return 0,10
                    
                    onay4 = row['kapanis'] >= row['acilis']                   


                    beyaz_kucuk =(row_son8_df['hesap_beyaz'] < 18).any()
                    kirmizi_kucuk =(row_son8_df['hesap_kirmizi'] < 22).any()
                    beyaz_kirmizi_kucuk =(row_son8_df['hesap_beyaz'] >= row_son8_df['hesap_kirmizi']).any()
                    beyaz_son = row['hesap_beyaz'] > 18
                    kirmizi_son = row['hesap_kirmizi'] > 22
                    onay1=beyaz_kucuk and kirmizi_kucuk and beyaz_kirmizi_kucuk and beyaz_son and kirmizi_son
                    if not onay1:
                       onay1= (row_son3_df['hesap_beyaz']>= row_son3_df['hesap_kirmizi']+27).any()

                 

                
                    rsi_values = df['RSI'].tail(2).tolist()
                    onay3 = len(rsi_values) == 2 and (rsi_values[1] >= rsi_values[0]-2)
                    mfi_values = df['mfi_oran'].tail(2).tolist()
                    onay6 = len(mfi_values) == 2 and (mfi_values[1] >= mfi_values[0]-2)
                    onay5=row['yesil_heiken'] 
                    

                    onay8 = (-100 <= row['CCI'] <= -1)


                    bb_ust = row['ust_band']
                    bb_alt = row['alt_band']
                    yuzde_fark = ((bb_ust - bb_alt) / bb_alt) * 100
                    onay11= 2.8>yuzde_fark>0.9

                    onay12 = row['kapanis'] < row['orta_band']

                    onay_13=(row_son4_df['DX']>35).any()
                
                  
                    
                    di_14 = df['+DI14'].tail(3).tolist()
                    di_14_ = df['-DI14'].tail(3).tolist()
                    onay_15 = len(di_14) == 3 and (di_14_[2]-di_14[2] <=di_14_[1]-di_14[1]   <= di_14_[0]-di_14[0])
                    dx = df['DX'].tail(6).tolist()
                    onay_16=round(dx[5],5)==round(dx[4],5) or round(dx[4],5)==round(dx[3],5) or round(dx[3],5)==round(dx[2],5) or round(dx[2],5)==round(dx[1],5) or round(dx[1],5)==round(dx[0],5) and round(dx[5],5)<=round(dx[4],5)
                    if not onay_16:
                        if row['DX']<=35 or dx[3]-25 > dx[5]:
                            onay_16=True


                    onay_17=(round(dx[5],5)==round(dx[4],5) or round(dx[4],5)==round(dx[3],5))
                    
                  
                    
                    onay_20=di_14[1] -1.5 <= di_14[2]
           
                    onay_21=row_son2_tek['DX'].iloc[0] >row['DX']
                   
                    onay_23=row['kapanis']>=row['acilis']
                    
                    onay_24=row['-DI14'] -4 >= row['+DI14']
                    onay_25=row['-DI14'] - row['+DI14']<=30
                  
                    onay_26=row['hesap_beyaz']<=45
                    onay_27=(row_son12_df['hesap_beyaz']>=85).any()
                    cci = df['CCI'].tail(3).tolist()
                    onay_28=cci[1]>=cci[0]+6 and cci[2]>=cci[1]+6
                    onay_29=row['CCI']>-100  
                    

                    if  onay_13 and onay_16 and onay_14 and onay_15 and onay_29 and onay_20 and onay_21 and onay_24 and onay_28  and onay_23 and onay_25 and  onay11 and onay_28:

                        return 1,6
                    if onay_17 and onay_18  and onay11 and onay_26 and onay_27 and onay_28 and onay_23:
                        return 1,20
                    
                           
                
                    if onay1   and onay3 and onay4  and onay6  and onay8 and onay10 and onay11 and onay12:

                            
                        if onay5:        
                                                                    
                            return 1,4                                              
                        else:                                                
                            return  7,10  
          

                    else:
                        
                        return  7,10  

                if row['hesap_beyaz'] >= 95:
                    return 0,10
                onay4 = row['kapanis'] > row['acilis']
                        
               
               

                beyaz_kucuk =(row_son8_df['hesap_beyaz'] < 8).any()
                kirmizi_kucuk=True
                beyaz_kirmizi_kucuk =(row_son8_df['hesap_beyaz'] >= row_son8_df['hesap_kirmizi']).any()
                beyaz_son = row['hesap_beyaz'] > 18
                kirmizi_son = row['hesap_kirmizi'] > 12
                onay1=beyaz_kucuk and beyaz_kirmizi_kucuk and beyaz_son and kirmizi_son
                if not onay1:
                    onay1= (row_son3_df['hesap_beyaz']>= row_son3_df['hesap_kirmizi']+27).any()

                rsi_values = df['RSI'].tail(3).tolist()
                onay3 = len(rsi_values) == 3 and (rsi_values[2] +15 >=rsi_values[1] +15 >= rsi_values[0])
                mfi_values = df['mfi_oran'].tail(3).tolist()
                onay6 = len(mfi_values) == 3 and (mfi_values[1]+15 >= mfi_values[1] +15 >= mfi_values[0])
                onay5=row['yesil_heiken'] 
                
                onay8 = (-100 <= row['CCI'] <= 10)


                onay10=(row['hesap_beyaz']<90)

                bb_ust = row['ust_band']
                bb_alt = row['alt_band']
                yuzde_fark = ((bb_ust - bb_alt) / bb_alt) * 100
                onay11=2.8>yuzde_fark>0.9

                onay12 = row['kapanis'] < row['orta_band']


                onay_100=(row_son4_df['DX']>35).any()

               
                di_14 = df['+DI14'].tail(3).tolist()
                di_14_ = df['-DI14'].tail(3).tolist()
                onay_103 = len(di_14) == 3 and (di_14_[2]-di_14[2] <=di_14_[1]-di_14[1]   <= di_14_[0]-di_14[0])
                
                dx = df['DX'].tail(6).tolist()
                onay_101=round(dx[5],5)==round(dx[4],5) or round(dx[4],5)==round(dx[3],5) or round(dx[3],5)==round(dx[2],5) or round(dx[2],5)==round(dx[1],5) or round(dx[1],5)==round(dx[0],5)

                if not onay_101:
                    if row['DX']<=35 or dx[3]-25 > dx[5]:
                        onay_101=True

                onay_104=di_14[1] -1.5 <= di_14[2]
                
                onay_105=round(row_son2_tek['DX'].iloc[0],5) > round(row['DX'],5)
              
                onay_107=row['kapanis']>row['acilis']
                
                onay_109=row['-DI14'] -4 >= row['+DI14']
                onay_110=row['-DI14'] - row['+DI14']<=30
               
             

                onay_121=(round(dx[5],5)==round(dx[4],5) or round(dx[4],5)==round(dx[3],5))

        
                onay_123=row['hesap_beyaz']<=45
                onay_124=(row_son12_df['hesap_beyaz']>=85).any()
                cci = df['CCI'].tail(3).tolist()
                onay_125=cci[1]>=cci[0]+6 and cci[2]>=cci[1]+6

                onay_126=row['CCI']>-100    
          
            
                if  onay_100 and onay_101  and onay_103 and onay_104 and onay_105 and onay_109  and onay_107 and onay_110  and  onay11 and onay_125 and onay_126:

                    return 1,6
                if onay_121  and onay11 and onay_123 and onay_124 and onay_125 and onay_107:
                    return 1,20

                if onay1   and onay3 and onay4  and onay6 and  onay8 and onay10 and onay11 and onay12 :
                                      
                    return 1,1                                                

                else:
                    
                    return  3,10  
            else:
                 return 3,10
            

            
