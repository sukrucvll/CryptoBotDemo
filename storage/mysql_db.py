import mysql.connector


def baglan_alis_satis():
    
    db=mysql.connector.connect(
        host="localhost",
        user="",
        password="",
        port=3307,
        database="alis_satis_islemleri")
    return db,db.cursor()
    

























