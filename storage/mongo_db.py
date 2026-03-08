import pymongo 

myclient=pymongo.MongoClient("mongodb://localhost:27017")

def get_db(isim:str):
    db_adi = f"{isim}_veri"
    return myclient[db_adi]


def hata_kaydet():
    
    mddb=myclient['hata']
    mongo= mddb['hata_collection']
    return mongo
def delete_database(isim: str):
    db_adi = f"{isim}_veri"
    myclient.drop_database(db_adi)
    print(f"{db_adi} -------- ")






