import aiohttp
import asyncio
import pandas as pd
from datetime import timedelta,datetime
from storage.mongo_db import get_db,hata_kaydet

import time
from api.binance_ import API_KEY

headers = {
    "X-MBX-APIKEY": API_KEY
}

columns = ['zaman_damgasi', 'acilis', 'yuksek', 'dusuk', 'kapanis', 'hacim', 
           'kapanis_zamani', 'teklif varlik_hacmi', 'islem_sayisi', 
           'alici_baz_hacmi', 'aliciteklif_hacmi', 'bakma']

async def get_binance_kline_async(session, symbol, interval='1m', limit=2):

    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol.upper()}&interval={interval}&limit={limit}"

    try:
        async with session.get(url, headers=headers) as response:
            data = await response.json()
            if not isinstance(data, list):
                print(f"{symbol} için veri alınamadı: {data}")
                return symbol, None
            
            df = pd.DataFrame(data, columns=columns)
            df.drop(columns=['bakma'], inplace=True)

            df['zaman_damgasi'] = pd.to_datetime(df['zaman_damgasi'], unit='ms') + timedelta(hours=3)
            df['kapanis_zamani'] = pd.to_datetime(df['kapanis_zamani'], unit='ms') + timedelta(hours=3)

            df['zaman_damgasi'] = df['zaman_damgasi'].dt.strftime('%Y-%m-%d %H:%M')
            df['kapanis_zamani'] = df['kapanis_zamani'].dt.strftime('%Y-%m-%d %H:%M')
            pd.set_option('display.float_format', lambda x: '%.8f' % x)
            df['kapanis'] = df['kapanis'].astype(float)
            df['yuksek'] = df['yuksek'].astype(float)
            df['dusuk'] = df['dusuk'].astype(float)
            df['acilis'] = df['acilis'].astype(float)
            df['hacim'] = df['hacim'].astype(float)
            

            return symbol, df[['zaman_damgasi', 'acilis', 'yuksek', 'dusuk', 'kapanis','kapanis_zamani','hacim']]
            # return symbol, df
    except Exception as e:
        mongo = hata_kaydet()
        timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
            
        hata = {
                'hata': str(e),
                'aciklama': f"data_fetcher sayfasında   '{symbol}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
        }
        mongo.insert_one(hata)
        return symbol, None

async def get_all_klines_async(coin_list, interval='1m', limit=2):
    async with aiohttp.ClientSession() as session:
        tasks = [get_binance_kline_async(session, coin, interval, limit) for coin in coin_list]
        results = await asyncio.gather(*tasks)
        return dict(results)
