import psycopg2 as pg
from psycopg2.extras import RealDictCursor
import os
import configparser as cfg
from datetime import datetime as dt
from datetime import timedelta


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


def insertIncome(userid, category, amount, desc, created_dt):
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
            cur.execute("INSERT INTO income (userid, category, amount, description, created_dt) "
                        "VALUES (%s, %s, %s, %s, %s);",
                        (userid, category, amount, desc, created_dt))
        conn.close()
    except Exception as e:
        print(e)
        print("Insert failed")


def showCatalogueDay(userid, created_dt):
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


def getDaySummary(userid, created_dt):
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
            cur.execute("""SELECT SUM(amount) as total, category FROM expenses 
            WHERE userid=%s AND created_dt=%s 
            GROUP BY category;""", (userid, created_dt))
            chosenDayRes = cur.fetchall()
            prevDay = dt.strptime(created_dt, "%Y-%m-%d") - timedelta(days=1)
            prevDate = prevDay.strftime("%Y-%m-%d")
            cur.execute("""SELECT SUM(amount) as total FROM expenses 
            WHERE userid=%s AND created_dt=%s;""", (userid, prevDate))
            prevDayRes = cur.fetchall()
        conn.close()
        if prevDayRes[0]['total'] is None:
            prevDayRes = []
        return chosenDayRes, prevDayRes
    except Exception as e:
        print(e)


def getMonthSummary(userid, year, month):
    prevYear, nextYear = year, year
    prevMonth, nextMonth = month - 1, month + 1
    if month == 12:
        nextYear = year + 1
        nextMonth = 1
    if month == 1:
        prevYear = year - 1
        prevMonth = 12
    current = dt(year=year, month=month, day=1)
    prev = dt(year=prevYear, month=prevMonth, day=1)
    next = dt(year=nextYear, month=nextMonth, day=1)
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
            cur.execute("""SELECT SUM(amount) as total, category FROM expenses 
            WHERE userid=%s AND created_dt >= %s AND created_dt < %s 
            GROUP BY category;""", (userid, current.strftime("%Y-%m-%d"), next.strftime("%Y-%m-%d")))
            chosenMonthRes = cur.fetchall()
            cur.execute("""SELECT SUM(amount) as total, category FROM expenses 
                        WHERE userid=%s AND created_dt >= %s AND created_dt < %s 
                        GROUP BY category;""", (userid, prev.strftime("%Y-%m-%d"), current.strftime("%Y-%m-%d")))
            prevMonthRes = cur.fetchall()
        conn.close()
        # if prevMonthRes[0]['total'] is None:
        #     prevDayRes = []
        return chosenMonthRes, prevMonthRes
    except Exception as e:
        print(e)