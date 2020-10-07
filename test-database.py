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


def insertExpense(userid, category, amount, desc, created_dt):
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
        with conn.cursor() as cur:
            cur.execute("INSERT INTO expenses (userid, category, amount, description, created_dt) "
                        "VALUES (%s, %s, %s, %s, %s);",
                        (userid, category, amount, desc, created_dt))
        conn.close()
    except Exception as e:
        print(e)
        print("Insert failed")



def showListDay(userid, created_dt):
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
            cur.execute("""SELECT * FROM expenses
                        WHERE userid=%s AND created_dt=%s;""", (userid, created_dt))
            res = cur.fetchall()
        conn.close()
        return res
    except Exception as e:
        print(e)
        print("Insert failed")


results = showListDay(137906605, '2020-10-05')     # Returns a list of
print(results)
for x in results:
    print(x['description'])