import MySQLdb

HOST="autofinancebot.mysql.pythonanywhere-services.com"
USER="autofinancebot"
PASSWD="Openshift!7"
DATABASE="autofinancebot$autofinance"

# db.query("""SELECT * FROM expenses""")
# r = db.store_result()
# result = r.fetch_row(maxrows=0)

db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE)
c = db.cursor()


def insertExpense(userid, category, desc, created_dt, amount):
    query = "INSERT INTO expenses (userid, category, description, created_dt, amount) " \
            "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), category, desc, created_dt, float(amount))
    c.execute(query)
    db.commit()


def insertIncome(userid, category, desc, created_dt, amount):
    query = "INSERT INTO income (userid, category, description, created_dt, amount) " \
            "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), category, desc, created_dt, float(amount))
    c.execute(query)
    db.commit()


def insertRecurring(userid, type, sched, desc, amount):
    query = "INSERT INTO recurring (userid, type, schedule, description, amount) " \
            "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), type, sched, desc, float(amount))
    c.execute(query)
    db.commit()


insertExpense("43", "gym", "tamp fitness", "2020-09-19", "2.50")
insertExpense("43", "gym", "tamp fitness", "2020-09-19", "2.50")
insertIncome("43", "gym", "tamp fitness", "2020-09-19", "2.50")
insertIncome("43", "gym", "tamp fitness", "2020-09-19", "2.50")
insertRecurring("43", "+", "3", "membership", "2.50")
insertRecurring("43", "-", "7", "salary", "3750")