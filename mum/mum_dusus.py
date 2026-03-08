import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storage.mongo_db import get_db
import pandas as pd
import time


def bearish_engulfing(df):
    df["onceki_acilis"] = df['acilis'].shift(1)
    df["onceki_kapanis"] = df['kapanis'].shift(1)

    df['bearish_engulfing'] = (
        (df['onceki_acilis'] < df['onceki_kapanis']) &   
        (df['acilis'] > df['kapanis']) &                
        (df['acilis'] > df['onceki_kapanis']) &         
        (df['kapanis'] < df['onceki_acilis'])
    )
    df['bearish_engulfing'] = df['bearish_engulfing'].fillna(False)
    return df
def inverted_hammer_bearish(df):
    df["govde"] = abs(df["kapanis"] - df["acilis"])
    df["fitil_ust"] = df["yuksek"] - df[["acilis", "kapanis"]].max(axis=1)
    df["fitil_alt"] = df[["acilis", "kapanis"]].min(axis=1) - df["dusuk"]

    df["inverted_hammer_bearish"] = (
        (df["fitil_ust"] >= df["govde"] * 1.8) &
        (df["fitil_alt"] <= df["govde"] * 0.35) &
        (df["kapanis"] < df["acilis"])
    )

    df["inverted_hammer_bearish"] = df["inverted_hammer_bearish"].fillna(False)
    return df

def three_black_crows(df):
    df["kapanis_1"] = df["kapanis"].shift(3)
    df["acilis_1"] = df["acilis"].shift(3)
    df["kapanis_2"] = df["kapanis"].shift(2)
    df["acilis_2"] = df["acilis"].shift(2)
    df["kapanis_3"] = df["kapanis"].shift(1)
    df["acilis_3"] = df["acilis"].shift(1)

    df["three_black_crows"] = (
        (df["kapanis_1"] < df["acilis_1"]) &  
        (df["kapanis_2"] < df["acilis_2"]) &  
        (df["kapanis_3"] < df["acilis_3"]) &  
        (df["acilis_3"] < df["kapanis_2"]) &  
        (df["kapanis"] < df["kapanis_1"])  
    )

    df["three_black_crows"] = df["three_black_crows"].fillna(False)
    return df


def hanging_man(df):
    govde = (df['kapanis'] - df['acilis']).abs()
    alt_fitil = ((df[['acilis', 'kapanis']]).min(axis=1)) - df['dusuk']
    ust_fitil = df['yuksek'] - (df[['acilis', 'kapanis']].max(axis=1))
    df['hanging_man'] = (
        (alt_fitil > govde * 2) & 
        (ust_fitil < govde) &      
        (df['kapanis'] < df['acilis']) 
    )
    df['hanging_man'] = df['hanging_man'].fillna(False)
    return df


def shooting_star(df):
    df["govde"] = abs(df["kapanis"] - df["acilis"])
    df["fitil_ust"] = df["yuksek"] - df[["acilis", "kapanis"]].max(axis=1)
    df["fitil_alt"] = df[["acilis", "kapanis"]].min(axis=1) - df["dusuk"]

    df["shooting_star"] = (
        (df["fitil_ust"] >= df["govde"] * 1.8) &    
        (df["fitil_alt"] <= df["govde"] * 0.35) & 
        (df["kapanis"] < df["acilis"])            
    )

    df["shooting_star"] = df["shooting_star"].fillna(False)
    return df


def evening_star(df):
    df["oncekli_acilis"] = df['acilis'].shift(1)
    df["oncekli_kapanis"] = df['kapanis'].shift(1)
    df["daha_oncekli_acilis"] = df['acilis'].shift(2)
    df["daha_oncekli_kapanis"] = df['kapanis'].shift(2)

    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["oncekli_kapanis"] = pd.to_numeric(df["oncekli_kapanis"], errors='coerce')
    df["oncekli_acilis"] = pd.to_numeric(df["oncekli_acilis"], errors='coerce')
    df["daha_oncekli_kapanis"] = pd.to_numeric(df["daha_oncekli_kapanis"], errors='coerce')
    df["daha_oncekli_acilis"] = pd.to_numeric(df["daha_oncekli_acilis"], errors='coerce')

    df['evening_star'] = (
        (df['daha_oncekli_kapanis'] > df['daha_oncekli_acilis']) &
        (abs(df['oncekli_acilis'] - df['oncekli_kapanis']) < abs(df['daha_oncekli_acilis'] - df['daha_oncekli_kapanis']) * 0.5) &  # 2. mum küçük
        (df['kapanis'] < df['acilis']) & 
        (df['kapanis'] < (df['daha_oncekli_acilis'] + df['daha_oncekli_kapanis']) / 2) 
    )
    df['evening_star'] = df['evening_star'].fillna(False)
    return df


def dark_cloud_cover(df):
    df["onceki_acilis"] = df['acilis'].shift(1)
    df["onceki_kapanis"] = df['kapanis'].shift(1)

    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["onceki_acilis"] = pd.to_numeric(df["onceki_acilis"], errors='coerce')
    df["onceki_kapanis"] = pd.to_numeric(df["onceki_kapanis"], errors='coerce')

    df['dark_cloud_cover'] = (
        (df['onceki_kapanis'] > df['onceki_acilis']) &  
        (df['acilis'] > df['onceki_kapanis']) & 
        (df['kapanis'] < (df['onceki_acilis'] + df['onceki_kapanis']) / 2) &  
        (df['kapanis'] < df['acilis'])  
    )
    df['dark_cloud_cover'] = df['dark_cloud_cover'].fillna(False)
    return df


def bearish_harami(df):
    df["onceki_acilis"] = df['acilis'].shift(1)
    df["onceki_kapanis"] = df['kapanis'].shift(1)

    df["acilis"] = pd.to_numeric(df["acilis"], errors='coerce')
    df["kapanis"] = pd.to_numeric(df["kapanis"], errors='coerce')
    df["onceki_kapanis"] = pd.to_numeric(df["onceki_kapanis"], errors='coerce')
    df["onceki_acilis"] = pd.to_numeric(df["onceki_acilis"], errors='coerce')

    df['bearish_harami'] = (
        (df['onceki_kapanis'] > df['onceki_acilis']) &  
        (df['acilis'] > df['kapanis']) &               
        (df['acilis'] < df['onceki_kapanis']) &       
        (df['kapanis'] > df['onceki_acilis'])
    )
    df['bearish_harami'] = df['bearish_harami'].fillna(False)
    return df


def falling_three_methods(df):
    df["acilis_1"] = df["acilis"].shift(4)
    df["kapanis_1"] = df["kapanis"].shift(4)

    df["acilis_2"] = df["acilis"].shift(3)
    df["kapanis_2"] = df["kapanis"].shift(3)

    df["acilis_3"] = df["acilis"].shift(2)
    df["kapanis_3"] = df["kapanis"].shift(2)

    df["acilis_4"] = df["acilis"].shift(1)
    df["kapanis_4"] = df["kapanis"].shift(1)

    df["falling_three_methods"] = (
        (df["kapanis_1"] < df["acilis_1"]) &  
        (df["kapanis_2"] > df["acilis_2"]) &  
        (df["kapanis_3"] > df["acilis_3"]) &  
        (df["kapanis_4"] > df["acilis_4"]) & 
        (df["acilis"] < df["acilis_4"]) &     
        (df["kapanis"] < df["kapanis_1"])   
    )

    df["falling_three_methods"] = df["falling_three_methods"].fillna(False)
    return df


def kicker_bearish(df):
    df["prev_open"] = df["acilis"].shift(1)
    df["prev_close"] = df["kapanis"].shift(1)

    df["kicker_bearish"] = (
        (df["prev_close"] > df["prev_open"]) & 
        (df["acilis"] < df["prev_open"]) &    
        (df["kapanis"] < df["acilis"])         
    )

    df["kicker_bearish"] = df["kicker_bearish"].fillna(False)
    return df


def mat_hold_bearish(df):
    df["a1"] = df["acilis"].shift(4)
    df["k1"] = df["kapanis"].shift(4)
    df["a2"] = df["acilis"].shift(3)
    df["k2"] = df["kapanis"].shift(3)
    df["a3"] = df["acilis"].shift(2)
    df["k3"] = df["kapanis"].shift(2)
    df["a4"] = df["acilis"].shift(1)
    df["k4"] = df["kapanis"].shift(1)

    df["mat_hold_bearish"] = (
        (df["k1"] < df["a1"]) & 
        (df["k2"] > df["a2"]) & (df["k3"] > df["a3"]) & (df["k4"] > df["a4"]) &  
        (df["kapanis"] < df["k1"])  
    )

    df["mat_hold_bearish"] = df["mat_hold_bearish"].fillna(False)
    return df


def breakaway_bearish(df):
    df["a1"] = df["acilis"].shift(4)
    df["k1"] = df["kapanis"].shift(4)
    df["a5"] = df["acilis"]
    df["k5"] = df["kapanis"]

    df["breakaway_bearish"] = (
        (df["k1"] > df["a1"]) &  
        (df["kapanis"].shift(3) > df["acilis"].shift(3)) &
        (df["kapanis"].shift(2) > df["acilis"].shift(2)) &
        (df["kapanis"].shift(1) > df["acilis"].shift(1)) &
        (df["k5"] < df["a5"]) &  
        (df["k5"] < df["a1"])    
    )

    df["breakaway_bearish"] = df["breakaway_bearish"].fillna(False)
    return df


def belt_hold_bearish(df):
    df["govde"] = abs(df["kapanis"] - df["acilis"])
    df["fitil_ust"] = df["yuksek"] - df[["acilis", "kapanis"]].max(axis=1)

    df["belt_hold_bearish"] = (
        (df["kapanis"] < df["acilis"]) & 
        (df["fitil_ust"] < df["govde"] * 0.1)
    )

    df["belt_hold_bearish"] = df["belt_hold_bearish"].fillna(False)
    return df


def three_line_strike_bearish(df):
    df["a1"] = df["acilis"].shift(3)
    df["k1"] = df["kapanis"].shift(3)
    df["a2"] = df["acilis"].shift(2)
    df["k2"] = df["kapanis"].shift(2)
    df["a3"] = df["acilis"].shift(1)
    df["k3"] = df["kapanis"].shift(1)

    df["three_line_strike_bearish"] = (
        (df["k1"] > df["a1"]) &
        (df["k2"] > df["a2"]) &
        (df["k3"] > df["a3"]) &
        (df["kapanis"] < df["a1"]) &  
        (df["acilis"] > df["k3"])
    )

    df["three_line_strike_bearish"] = df["three_line_strike_bearish"].fillna(False)
    return df


def mum_teyit_ust(coin, df):
    """
    Normal mum teyit fonksiyonu - Tüm mum analizlerini yapar ve DataFrame'e ekler
    """
    
    df_analiz = df.copy()
    
    df_analiz = bearish_engulfing(df_analiz)
    df_analiz = inverted_hammer_bearish(df_analiz)
    df_analiz = three_black_crows(df_analiz)
    df_analiz = hanging_man(df_analiz)
    df_analiz = shooting_star(df_analiz)
    df_analiz = evening_star(df_analiz)
    df_analiz = dark_cloud_cover(df_analiz)
    df_analiz = bearish_harami(df_analiz)
    df_analiz = falling_three_methods(df_analiz)
    df_analiz = kicker_bearish(df_analiz)
    df_analiz = mat_hold_bearish(df_analiz)
    df_analiz = breakaway_bearish(df_analiz)
    df_analiz = belt_hold_bearish(df_analiz)
    df_analiz = three_line_strike_bearish(df_analiz)

    df_birlesik = pd.merge(
    df.drop(columns=[c for c in df.columns if c in [
        'bearish_engulfing','inverted_hammer_bearish','three_black_crows',
        'hanging_man','shooting_star','evening_star','dark_cloud_cover',
        'bearish_harami','falling_three_methods','kicker_bearish',
        'mat_hold_bearish','breakaway_bearish','belt_hold_bearish',
        'three_line_strike_bearish'
    ]], errors="ignore"),
    df_analiz[['zaman_damgasi','bearish_engulfing','inverted_hammer_bearish','three_black_crows',
        'hanging_man','shooting_star','evening_star','dark_cloud_cover',
        'bearish_harami','falling_three_methods','kicker_bearish',
        'mat_hold_bearish','breakaway_bearish','belt_hold_bearish',
        'three_line_strike_bearish']],
    on='zaman_damgasi',
    how='left'
)
    
    son_4 = df_birlesik.iloc[-4:]

    bearish_cols = [
        'bearish_engulfing','inverted_hammer_bearish','three_black_crows',
        'hanging_man','shooting_star','evening_star','dark_cloud_cover',
        'bearish_harami','falling_three_methods','kicker_bearish',
        'mat_hold_bearish','breakaway_bearish','belt_hold_bearish',
        'three_line_strike_bearish'
    ]

    true_patterns = []
    for col in bearish_cols:
        if son_4[col].any():  
            df_birlesik.loc[df_birlesik.index[-4:] , col] = True
            
            true_patterns.append(col)

    if true_patterns:
        return True, df_birlesik
    else:
        return False, df_birlesik
    
    