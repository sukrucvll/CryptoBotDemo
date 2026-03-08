import time
from storage.mongo_db import get_db
from datetime import datetime, timedelta,timezone
from storage.mongo_db import hata_kaydet

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.last_saved = {}

    def update_cache(self, coin, new_data):
        old_data = self.cache.get(coin, {}).get("data")
       
   
        if old_data is None or new_data["zaman_damgasi"].iloc[-1] != old_data["zaman_damgasi"].iloc[-1]:
            self.cache[coin] = {
                "data": new_data,
                "timestamp": time.time()
            }

        now = time.time()
        last_saved_coin = self.last_saved.get(coin, 0)
       

        if now - last_saved_coin >= 55:
            self.last_saved[coin] = now  
            self.save_to_mongo(coin, new_data)
    def save_to_mongo(self, coin, new_data):
        try:
            data_to_save = new_data.to_dict('records')

            mydb = get_db(coin)
            koleksiyon_adi = coin + "_1m_veri"
            mycollection = mydb[koleksiyon_adi]

            last_record = mycollection.find_one(sort=[("zaman_damgasi", -1)])
            if last_record:
                last_time = last_record["zaman_damgasi"]
                data_to_save = [row for row in data_to_save if row["zaman_damgasi"] > last_time]

            if data_to_save:
                mycollection.insert_many(data_to_save)
                turkiye_saati = datetime.now(timezone(timedelta(hours=3)))
                turkiye_sade = turkiye_saati.replace(second=0, microsecond=0, tzinfo=None)

        

                dk_once = turkiye_sade - timedelta(minutes=90)
                dk_once_str = dk_once.strftime("%Y-%m-%d %H:%M")
            
                mycollection.delete_many({
                "zaman_damgasi": {"$lt": dk_once_str}
                })
                
            else:
                print(f"***********{coin} için yeni veri bulunamadı, MongoDB'ye kayıt yapılmadı.*******************")
        
        except Exception as e:

            mongo = hata_kaydet()
            timestamp = time.time()
            dt = datetime.fromtimestamp(timestamp)
            
            hata = {
                'hata': str(e),
                'aciklama': f"cache_manager fonkisiyonunda  '{coin}' icin hata olustu.",
                'zaman': dt.strftime("%Y-%m-%d %H:%M:%S")
            }
            mongo.insert_one(hata)
    def get_cache(self, coin):
        return self.cache.get(coin, None)

    def is_fresh(self, coin, freshness_limit=10):
               
        entry = self.get_cache(coin)
        if entry:
            return (time.time() - entry["timestamp"]) < freshness_limit
        return False





