import psycopg2 as pg
from psycopg2.extras import RealDictCursor
import os
import configparser as cfg


try:
    config = cfg.ConfigParser()
    config.read("config.cfg")
    HOST = config.get("creds", "HOST")
    DATABASE = config.get("creds", "DATABASE")
    USER = config.get("creds", "USER")
    PASSWORD = config.get("creds", "PASSWD")
except:
    pass

def showSummaryDay():
    try:
        DATABASE_URL = os.environ['DATABASE_URL']
        conn = pg.connect(
            DATABASE_URL,
            sslmode='require'
        )
    except Exception as e:
        conn = pg.connect(
            host=HOST,
            database=DATABASE,
            user=USER,
            password=PASSWORD
        )
    try:
        conn.set_session(autocommit=True)
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""SELECT * FROM expenses;""")
            res = cur.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(e)
        print("Insert failed")


results = showSummaryDay()     # Returns a list of
for x in results:
    print(x['description'])