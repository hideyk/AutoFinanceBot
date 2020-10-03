import psycopg2 as pg
import os


def insertExpense(userid, category, amount, desc, created_dt):
    try:
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = pg.connect(
                DATABASE_URL,
                sslmode='require'
            )
        except:
            conn = pg.connect(
                host="localhost",
                database="autofinance-bot",
                user="postgres",
                password="hideyuki1994"
            )
        query = "INSERT INTO expenses (userid, category, description, created_dt, amount) " \
                "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), category, desc, created_dt, float(amount))
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Insert failed")
        print(e)

def insertIncome(userid, category, amount, desc, created_dt):
    # conn = pg.connect(
    #     DATABASE_URL,
    #     sslmode='require'
    # )
    try:
        conn = pg.connect(
            host="localhost",
            database="autofinance-bot",
            user="postgres",
            password="hideyuki1994"
        )
        query = "INSERT INTO income (userid, category, description, created_dt, amount) " \
                "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), category, desc, created_dt, float(amount))
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Insert failed")
