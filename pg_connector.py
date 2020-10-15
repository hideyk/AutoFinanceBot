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


def insertNewUser(userid, firstname):
    now = dt.utcnow() + timedelta(hours=8)
    joindate = now.strftime("%Y-%m-%d")
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
            cur.execute("SELECT * FROM users WHERE userid=%s;", [userid])
            userdetails = cur.fetchall()
            if not userdetails:
                cur.execute("INSERT INTO users (userid, firstName, joinDate) "
                            "VALUES (%s, %s, %s);",
                            (userid, firstname, joindate))
    except Exception as e:
        print(e)
    conn.close()


def upgradeToPremium(userid):
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
            cur.execute("SELECT isPremium FROM users WHERE userid=%s;", [userid])
            result = cur.fetchall()
            if not result:
                conn.close()
                return False, True
            userIsPremium = result[0][0]
            if not userIsPremium:
                conn.close()
                return False, False
            else:
                conn.close()
                return True, False
    except Exception as e:
        print(e)


def checkPremium(userid):
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
            cur.execute("SELECT isPremium FROM users WHERE userid=%s;", [userid])
            result = cur.fetchall()
            if not result:
                conn.close()
                return False, True
            userIsPremium = result[0][0]
            if not userIsPremium:
                conn.close()
                return False, False
            else:
                conn.close()
                return True, False
    except Exception as e:
        print(e)


def checkValidPromocode(promo_code):
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
            cur.execute("SELECT used FROM promocodes WHERE promocode=%s;", [promo_code])
            result = cur.fetchall()
            if not result:
                conn.close()
                return False, True
            promoIsUsed = result[0][0]
            if promoIsUsed:
                conn.close()
                return False, False
            else:
                conn.close()
                return True, False
    except Exception as e:
        print(e)


def checkDailyLimit(inputType, userid, expenseDate):
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
            if inputType == "expense":
                cur.execute("SELECT COUNT(*) FROM expenses "
                            "WHERE userid=%s AND "
                            "created_dt=%s;", (userid, expenseDate))
            if inputType == "income":
                cur.execute("SELECT COUNT(*) FROM income "
                            "WHERE userid=%s AND "
                            "created_dt=%s;", (userid, expenseDate))
            result = cur.fetchall()
        conn.close()
        return result[0][0]
    except Exception as e:
        conn.close()


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
        return False
    except Exception as e:
        conn.close()
        return True


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
        return False
    except Exception as e:
        conn.close()
        return True


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
        return res
    except Exception as e:
        print(e)
    conn.close()


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
        if prevDayRes[0]['total'] is None:
            prevDayRes = []
        return chosenDayRes, prevDayRes
    except Exception as e:
        print(e)
    conn.close()


def getWeekSummary(userid, selected_date):
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
            cur.execute("""SELECT SUM(amount) AS total, category 
                        FROM expenses WHERE userid=%s AND 
                        to_char(created_dt, 'iyyy-iw') = to_char(date %s, 'iyyy-iw') 
                        GROUP BY category;""", (userid, selected_date))
            chosenWeekRes = cur.fetchall()
            prevWeekDay = dt.strptime(selected_date, "%Y-%m-%d") - timedelta(days=7)
            prevWeekDate = prevWeekDay.strftime("%Y-%m-%d")
            cur.execute("""SELECT SUM(amount) AS total, category 
                        FROM expenses WHERE userid=%s AND 
                        to_char(created_dt, 'iyyy-iw') = to_char(date %s, 'iyyy-iw') 
                        GROUP BY category;""", (userid, prevWeekDate))
            prevWeekRes = cur.fetchall()
        if prevWeekRes:
            if prevWeekRes[0]['total'] is None:
                prevWeekRes = []
        return chosenWeekRes, prevWeekRes
    except Exception as e:
        print(e)
    conn.close()


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
        return chosenMonthRes, prevMonthRes
    except Exception as e:
        print(e)
    conn.close()