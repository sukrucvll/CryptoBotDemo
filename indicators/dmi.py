import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import datetime
import pandas as pd
import numpy as np
from binance.client import Client
from  api.binance_ import bagla
from storage.mongo_db import get_db,hata_kaydet
import time



class DMI:
    
    def __init__(self, name,zaman_dilimi,period):
        self.name=name
        self.zaman_dilimi=zaman_dilimi
        self.period = period

       
    def dmi_hesaplama_islem_md(self, df):
        try:
            up_move   = df['yuksek'] - df['yuksek'].shift(1)
            down_move = df['dusuk'].shift(1) - df['dusuk']

            df['+DM'] = np.where(
                (up_move > down_move) & (up_move > 0),
                up_move, 0.0
            )

            df['-DM'] = np.where(
                (down_move > up_move) & (down_move > 0),
                down_move, 0.0
            )

            tr1 = df['yuksek'] - df['dusuk']
            tr2 = (df['yuksek'] - df['kapanis'].shift(1)).abs()
            tr3 = (df['dusuk'] - df['kapanis'].shift(1)).abs()

            df['TR'] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            df['TR14']   = self.rma(df['TR'], self.period)
            df['+DM14']  = self.rma(df['+DM'], self.period)
            df['-DM14']  = self.rma(df['-DM'], self.period)

            df['+DI14'] = 100 * (df['+DM14'] / df['TR14'])
            df['-DI14'] = 100 * (df['-DM14'] / df['TR14'])

            di_sum = df['+DI14'] + df['-DI14']
            df['DX'] = np.where(
                di_sum == 0,
                0,
                100 * (abs(df['+DI14'] - df['-DI14']) / di_sum)
            )

            df['ADX'] = self.rma(df['DX'], self.period)

            df.drop(
                columns=['+DM','-DM','TR','TR14','+DM14','-DM14'],
                inplace=True
            )

            return df

        except Exception as e:
            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.datetime.fromtimestamp(timestamp)

            mongo.insert_one({
                'hata': str(e),
                'aciklama': f"dmi_hesaplama_islem_md içinde '{self.name}' için hata",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            })
            return df

   
    @staticmethod
    def rma(series: pd.Series, period: int):
        rma = pd.Series(index=series.index, dtype='float64')

        # TradingView seed: first period SMA
        rma.iloc[period-1] = series.iloc[:period].mean()

        # Wilder smoothing
        for i in range(period, len(series)):
            rma.iloc[i] = (rma.iloc[i-1] * (period - 1) + series.iloc[i]) / period

        return rma

   