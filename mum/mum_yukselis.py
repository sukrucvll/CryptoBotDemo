import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mongo_db import get_db
import pandas as pd
import time




def hacim(df):

    df["hacim_farki"] = df["hacim"] / df["hacim"].rolling(5).mean()
    df["hacim_deger"] = df["hacim_farki"] > 1.15
    return df

def bullish_engulfing(df):
    df["oncekli_acilis"]=df['acilis'].shift(1)
    df["oncekli_kapanis"]=df['kapanis'].shift(1)
    
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
    df["onceki_dusus_yuzdesi"] = (
          abs((df["oncekli_acilis"] - df["oncekli_kapanis"]) / df["oncekli_acilis"])
      )

    
    df['bullish_engulfing'] = (
    (df['oncekli_acilis'] > df['oncekli_kapanis']) &   
    (df['acilis'] < df['kapanis']) &                  
    (df['acilis'] < df['oncekli_kapanis']) &           
    (df['kapanis'] > df['oncekli_acilis']) &          
    (df["onceki_dusus_yuzdesi"] > 0.002)
     )
    df['bullish_engulfing'] = df['bullish_engulfing'].fillna(False)
    return df    
def haykin(df):

    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    
    df['ha_kapanis'] = (df['acilis'] + df['kapanis'] + df['yuksek'] + df['dusuk']) / 4

    ha_open = [df['acilis'].iloc[0]]  

    for i in range(1, len(df)):
        ha_open.append((ha_open[i - 1] + df['ha_kapanis'].iloc[i - 1]) / 2)

    df['ha_acilis'] = ha_open

    df['ha_yuksek'] = df[['yuksek', 'ha_acilis', 'ha_kapanis']].max(axis=1)
    df['ha_dusuk']  = df[['dusuk', 'ha_acilis', 'ha_kapanis']].min(axis=1)

    df['yesil'] = df['ha_kapanis'] > df['ha_acilis']
    df['kirmizi'] = df['ha_kapanis'] < df['ha_acilis']
    
    return df

def uc_asker(df):

    df["oncekli_kapanis1"]=df['kapanis'].shift(1)
    df["oncekli_acilis1"]=df['acilis'].shift(1)
    df["oncekli_acilis2"]=df['acilis'].shift(2)
    df["oncekli_kapanis2"]=df['kapanis'].shift(2)

    pd.set_option('display.float_format', lambda x: '%.8f' % x) 
    df[["acilis", "kapanis", "oncekli_kapanis1", "oncekli_acilis1", "oncekli_kapanis2", "oncekli_acilis2"]] = df[["acilis", "kapanis", "oncekli_kapanis1", "oncekli_acilis1", "oncekli_kapanis2", "oncekli_acilis2"]].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    
    df["uc_asker"] = (
    (df["oncekli_kapanis2"] > df["oncekli_acilis2"]) &  
    ((df["oncekli_kapanis2"] - df["oncekli_acilis2"]) / df["oncekli_acilis2"] > 0.0012) &  
    
    (df["oncekli_kapanis1"] > df["oncekli_acilis1"]) &
    (df["oncekli_acilis1"] > df["oncekli_kapanis2"]) &
    ((df["oncekli_kapanis1"] - df["oncekli_acilis1"]) / df["oncekli_acilis1"] > 0.0012) &
    
    (df["kapanis"] > df["acilis"]) &
    (df["acilis"] > df["oncekli_kapanis1"]) &
    ((df["kapanis"] - df["acilis"]) / df["acilis"] > 0.0012)
        
        )
    df["uc_asker"] = df["uc_asker"].fillna(False)
    return df  


def ayi_mumu_mu(df):

    df["oncekli_kapanis1"]=df['kapanis'].shift(1)
    df["oncekli_acilis1"]=df['acilis'].shift(1)
    df["oncekli_acilis2"]=df['acilis'].shift(2)
    df["oncekli_kapanis2"]=df['kapanis'].shift(2)

    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    df[["acilis", "kapanis", "oncekli_kapanis1", "oncekli_acilis1", "oncekli_kapanis2", "oncekli_acilis2"]] = df[["acilis", "kapanis", "oncekli_kapanis1", "oncekli_acilis1", "oncekli_kapanis2", "oncekli_acilis2"]].apply(lambda x: pd.to_numeric(x, errors='coerce'))
    
    df["ayi_mu"]=((df['oncekli_acilis2']>df['oncekli_kapanis2']) & (df['acilis']<df['kapanis']) 
                  & (((abs((df['oncekli_kapanis2']*100)/df['oncekli_acilis2']-100))>0.1))
                  & (((abs((df['oncekli_kapanis1']*100)/df['oncekli_acilis1']-100))<0.02))
                  & (df['oncekli_acilis2'] > df['kapanis'])
                  & (df['oncekli_kapanis2'] > df['acilis'])
                  )
    df["ayi_mu"] = df["ayi_mu"].fillna(False)
    return df  

def tweezer_bottom(df):
 
    df["oncekli_kapanis1"]=df['kapanis'].shift(1)
    df["oncekli_acilis2"]=df['acilis'].shift(2)
    df["oncekli_kapanis2"]=df['kapanis'].shift(2)
 
    df["oncekli_kapanis2"] = pd.to_numeric(df["oncekli_kapanis2"], errors='coerce')
    df["oncekli_kapanis1"] = pd.to_numeric(df["oncekli_kapanis1"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["oncekli_acilis2"] = pd.to_numeric(df["oncekli_acilis2"], errors='coerce')
    
    df['tweezer_bottom']=(
         (df["oncekli_acilis2"]>df["oncekli_kapanis2"]) & ((abs((df["oncekli_kapanis2"]*100)/df["oncekli_kapanis1"]-100))<0.05) &
                          (((abs((df["oncekli_kapanis1"]*100)/df["kapanis"]-100))<0.05) & ((abs((df["oncekli_kapanis2"]*100)/df["kapanis"]-100))<0.05))
                          )
    df['tweezer_bottom'] = df['tweezer_bottom'].fillna(False)
    return df

def dragonfly(df):

   
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
       
    df['dragonfly'] = (
        (abs(df['acilis'] - df['kapanis']) < (df['acilis'] * 0.0009)) &
        (df['yuksek'] - df['acilis'] < (df['acilis'] * 0.002)) &
        ((df['acilis'] - df['dusuk']) > (df['acilis'] * 0.008))
    )
    df['dragonfly'] = df['dragonfly'].fillna(False)

    return df 


def bullish_harami(df):
    df["oncekli_acilis"] = df['acilis'].shift(1)  
    df["oncekli_kapanis"] = df['kapanis'].shift(1) 
   
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["oncekli_kapanis"] = pd.to_numeric(df["oncekli_kapanis"], errors='coerce')
    df["oncekli_acilis"] = pd.to_numeric(df["oncekli_acilis"], errors='coerce')
  
    
    df['bullish_harami'] = (
        (df['onceki_kapanis'] < df['onceki_acilis']) &
        (df['acilis'] > df['onceki_kapanis']) &
        (df['kapanis'] < df['onceki_acilis']) &
        (df['kapanis'] > df['acilis'])  
    )
    df['bullish_harami'] = df['bullish_harami'].fillna(False)

    return df 

def doji_star(df):
    df["onceki_acilis"] = df['acilis'].shift(1)
    df["onceki_kapanis"] = df['kapanis'].shift(1)

    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["onceki_acilis"] = pd.to_numeric(df["onceki_acilis"], errors='coerce')
    df["onceki_kapanis"] = pd.to_numeric(df["onceki_kapanis"], errors='coerce')

    doji_threshold = 0.001

    df['doji_star'] = (
        (df['onceki_kapanis'] < df['onceki_acilis']) & 
        (abs(df['acilis'] - df['kapanis']) <= (df['acilis'] * doji_threshold)) &  
        (df['kapanis'] > df['acilis'])  
    )

    df['doji_star'] = df['doji_star'].fillna(False)

    return df



def piercing_pattern(df):
    df["onceki_acilis"] = df['acilis'].shift(1)
    df["onceki_kapanis"] = df['kapanis'].shift(1)

    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["onceki_acilis"] = pd.to_numeric(df["onceki_acilis"], errors='coerce')
    df["onceki_kapanis"] = pd.to_numeric(df["onceki_kapanis"], errors='coerce')

    df['piercing_pattern'] = (
        (df['onceki_kapanis'] < df['onceki_acilis']) &  
        (df['acilis'] < df['onceki_kapanis']) &  
        (df['kapanis'] > (df['onceki_acilis'] + df['onceki_kapanis']) / 2) &  
        (df['kapanis'] > df['acilis'])  
    )

    df['piercing_pattern'] = df['piercing_pattern'].fillna(False)
    return df


def morning_star(df):
    df["oncekli_acilis"] = df['acilis'].shift(1) 
    df["oncekli_kapanis"] = df['kapanis'].shift(1)  
    df["daha_oncekli_acilis"] = df['acilis'].shift(2) 
    df["daha_oncekli_kapanis"] = df['kapanis'].shift(2)  
   
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["oncekli_kapanis"] = pd.to_numeric(df["oncekli_kapanis"], errors='coerce')
    df["oncekli_acilis"] = pd.to_numeric(df["oncekli_acilis"], errors='coerce')
    df["daha_oncekli_kapanis"] = pd.to_numeric(df["daha_oncekli_kapanis"], errors='coerce')
    df["daha_oncekli_acilis"] = pd.to_numeric(df["daha_oncekli_acilis"], errors='coerce')
  
    
    df['morning_star'] = (
        (df['daha_oncekli_kapanis'] < df['daha_oncekli_acilis']) & 
        (abs(df['oncekli_acilis'] - df['oncekli_kapanis']) < abs(df['daha_oncekli_acilis'] - df['daha_oncekli_kapanis']) * 0.5) &  # 2. mum küçük
        (df['kapanis'] > df['acilis']) &  
        (df['kapanis'] > (df['daha_oncekli_acilis'] + df['daha_oncekli_kapanis']) / 2)  
    )
    df['morning_star'] = df['morning_star'].fillna(False)
    return df 


def benim_formasyon(df):
    df["oncekli_acilis"] = df['acilis'].shift(1)  
    df["oncekli_kapanis"] = df['kapanis'].shift(1) 
   
    pd.set_option('display.float_format', lambda x: '%.8f' % x)
    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["oncekli_kapanis"] = pd.to_numeric(df["oncekli_kapanis"], errors='coerce')
    df["oncekli_acilis"] = pd.to_numeric(df["oncekli_acilis"], errors='coerce')
  
    
    df['benim_formasyon'] = (
        (((df['oncekli_acilis'] + df['oncekli_kapanis']) / 2) <= df['acilis']) &
        (df['acilis'] < df['kapanis']) &
        (df['oncekli_acilis'] > df['oncekli_kapanis']) &
        (df['kapanis'] > df['oncekli_acilis'])
        )
    df['benim_formasyon'] = df['benim_formasyon'].fillna(False)
    return df 

def hammer(df):
    govde = (df['acilis'] - df['kapanis']).abs()
    alt_fitil= ((df[['acilis','kapanis']]).min(axis=1))-df['dusuk']
    ust_fitil= df['yuksek']-(df[['acilis','kapanis']].max(axis=1))
    df['hammer'] = (alt_fitil > govde * 2) & (ust_fitil < govde)
    df['hammer'] = df['hammer'].fillna(False)
    return df

def inverted_hammer(df):
    df["govde"] = abs(df["kapanis"] - df["acilis"])
    df["fitil_ust"] = df["yuksek"] - df[["acilis", "kapanis"]].max(axis=1)
    df["fitil_alt"] = df[["acilis", "kapanis"]].min(axis=1) - df["dusuk"]

    df["inverted_hammer"] = (
        (df["fitil_ust"] >= df["govde"] * 1.8) &
        (df["fitil_alt"] <= df["govde"] * 0.35)
    )

    df["inverted_hammer"] = df["inverted_hammer"].fillna(False)
    return df

def rising_three_methods(df):
    df["acilis_1"] = df["acilis"].shift(4)
    df["kapanis_1"] = df["kapanis"].shift(4)

    df["acilis_2"] = df["acilis"].shift(3)
    df["kapanis_2"] = df["kapanis"].shift(3)

    df["acilis_3"] = df["acilis"].shift(2)
    df["kapanis_3"] = df["kapanis"].shift(2)

    df["acilis_4"] = df["acilis"].shift(1)
    df["kapanis_4"] = df["kapanis"].shift(1)

    df["rising_three_methods"] = (
        (df["kapanis_1"] > df["acilis_1"]) &  
        (df["kapanis_2"] < df["acilis_2"]) &  
        (df["kapanis_3"] < df["acilis_3"]) &  
        (df["kapanis_4"] < df["acilis_4"]) &  
        (df["acilis"] > df["acilis_4"]) &     
        (df["kapanis"] > df["kapanis_1"])     
    )

    df["rising_three_methods"] = df["rising_three_methods"].fillna(False)
    return df


def kicker_bullish(df):
    df["prev_open"] = df["acilis"].shift(1)
    df["prev_close"] = df["kapanis"].shift(1)

    df["kicker_bullish"] = (
        (df["prev_close"] < df["prev_open"]) &  
        (df["acilis"] > df["prev_open"]) &      
        (df["kapanis"] > df["acilis"])          
    )

    df["kicker_bullish"] = df["kicker_bullish"].fillna(False)
    return df

def mat_hold_bullish(df):
    df["a1"] = df["acilis"].shift(4)
    df["k1"] = df["kapanis"].shift(4)
    df["a2"] = df["acilis"].shift(3)
    df["k2"] = df["kapanis"].shift(3)
    df["a3"] = df["acilis"].shift(2)
    df["k3"] = df["kapanis"].shift(2)
    df["a4"] = df["acilis"].shift(1)
    df["k4"] = df["kapanis"].shift(1)

    df["mat_hold_bullish"] = (
        (df["k1"] > df["a1"]) &  
        (df["k2"] < df["a2"]) & (df["k3"] < df["a3"]) & (df["k4"] < df["a4"]) &  
        (df["kapanis"] > df["k1"])  
    )

    df["mat_hold_bullish"] = df["mat_hold_bullish"].fillna(False)
    return df

def breakaway_bullish(df):
    df["a1"] = df["acilis"].shift(4)
    df["k1"] = df["kapanis"].shift(4)
    df["a5"] = df["acilis"]
    df["k5"] = df["kapanis"]

    df["breakaway_bullish"] = (
        (df["k1"] < df["a1"]) &  
        (df["kapanis"].shift(3) < df["acilis"].shift(3)) &
        (df["kapanis"].shift(2) < df["acilis"].shift(2)) &
        (df["kapanis"].shift(1) < df["acilis"].shift(1)) &
        (df["k5"] > df["a5"]) &  l
        (df["k5"] > df["a1"])    
    )

    df["breakaway_bullish"] = df["breakaway_bullish"].fillna(False)
    return df

def belt_hold_bullish(df):
    df["govde"] = abs(df["kapanis"] - df["acilis"])
    df["fitil_alt"] = df[["acilis", "kapanis"]].min(axis=1) - df["dusuk"]

    df["belt_hold_bullish"] = (
        (df["kapanis"] > df["acilis"]) &  
        (df["fitil_alt"] < df["govde"] * 0.1)  
    )

    df["belt_hold_bullish"] = df["belt_hold_bullish"].fillna(False)
    return df


def three_line_strike_bullish(df):
    df["a1"] = df["acilis"].shift(3)
    df["k1"] = df["kapanis"].shift(3)
    df["a2"] = df["acilis"].shift(2)
    df["k2"] = df["kapanis"].shift(2)
    df["a3"] = df["acilis"].shift(1)
    df["k3"] = df["kapanis"].shift(1)

    df["three_line_strike_bullish"] = (
        (df["k1"] < df["a1"]) &
        (df["k2"] < df["a2"]) &
        (df["k3"] < df["a3"]) &
        (df["kapanis"] > df["a1"]) & 
        (df["acilis"] < df["k3"])
    )

    df["three_line_strike_bullish"] = df["three_line_strike_bullish"].fillna(False)
    return df



def mum_teyit_alt(coin, df):
    """
    Normal mum teyit fonksiyonu - Tüm mum analizlerini yapar ve DataFrame'e ekler
    """
    print(f"{coin} - Mum teyit fonksiyonu çağrıldı")
    
    df_analiz = df.copy()
    

    # df_analiz = hammer(df_analiz)
    # df_analiz = inverted_hammer(df_analiz)
    df_analiz = rising_three_methods(df_analiz)
    # df_analiz = kicker_bullish(df_analiz)
    # df_analiz = mat_hold_bullish(df_analiz)
    # df_analiz = breakaway_bullish(df_analiz)
    # df_analiz = belt_hold_bullish(df_analiz)
    # df_analiz = three_line_strike_bullish(df_analiz)
    # df_analiz = benim_formasyon(df_analiz)
    # df_analiz = morning_star(df_analiz)
    # df_analiz = piercing_pattern(df_analiz)  b
    # df_analiz = doji_star(df_analiz)
    # df_analiz = bullish_harami(df_analiz)
    # df_analiz = dragonfly(df_analiz)
    df_analiz = bullish_engulfing(df_analiz)
    # df_analiz = hacim(df_analiz)
    df_analiz = uc_asker(df_analiz)
    df_analiz = ayi_mumu_mu(df_analiz)
    df_analiz = tweezer_bottom(df_analiz)

    df_birlesik = pd.merge(
    df.drop(columns=[c for c in df.columns if c in [
        'tweezer_bottom',
        'ayi_mu',
        'uc_asker',
        'bullish_engulfing',
        'rising_three_methods'
       
    ]], errors="ignore"),
    df_analiz[['zaman_damgasi',
               'tweezer_bottom',
        'ayi_mu',
        'uc_asker',
        'bullish_engulfing',
        'rising_three_methods']],
    on='zaman_damgasi',
    how='left'
)
    son_4 = df_birlesik.iloc[-4:]

    pattern_cols = [
        'tweezer_bottom',
        'ayi_mu',
        'uc_asker',
        'bullish_engulfing',
        'rising_three_methods'
    ]

    true_patterns = []
    for col in pattern_cols:
        if son_4[col].any():  
            df_birlesik.loc[df_birlesik.index[-4:], col] = True
            true_patterns.append(col)

    if true_patterns:
        print(f"{coin} - Mum teyit onaylandı! ({len(true_patterns)} pattern bulundu: {', '.join(true_patterns)})")
       
        return True, df_birlesik
    else:
        print(f"{coin} - Mum teyit onaylanmadı. (Hiç pattern bulunamadı)")
        return False, df_birlesik
    

