import pymongo 

myclient=pymongo.MongoClient("mongodb://localhost:27017")


veriler = [db for db in myclient.list_database_names() if db.endswith("_veri")]


def delete_database_tam(isim: str):
    db_adi = f"{isim}"
    myclient.drop_database(db_adi)
    print(f"{db_adi} ")

for i in veriler:
    delete_database_tam(i)

exit()
