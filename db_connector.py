import MySQLdb
import configparser as cfg

config = cfg.ConfigParser()
config.read("config.cfg")
HOST = config.get("creds", "HOST")
USER = config.get("creds", "USER")
PASSWD = config.get("creds", "PASSWD")
DATABASE = config.get("creds", "DATABASE")

# db.query("""SELECT * FROM expenses""")
# r = db.store_result()
# result = r.fetch_row(maxrows=0)

try:
    db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DATABASE)
    c = db.cursor()
except Exception as e:
    print("Can't connect to DB")
    print(e)
    exit()


def insertExpense(userid, category, amount, desc, created_dt):
    query = "INSERT INTO expenses (userid, category, description, created_dt, amount) " \
            "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), category, desc, created_dt, float(amount))
    c.execute(query)
    db.commit()


def insertIncome(userid, category, amount, desc, created_dt):
    query = "INSERT INTO income (userid, category, description, created_dt, amount) " \
            "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), category, desc, created_dt, float(amount))
    c.execute(query)
    db.commit()


def insertRecurring(userid, type, sched, desc, amount):
    query = "INSERT INTO recurring (userid, type, schedule, description, amount) " \
            "VALUES (%s, '%s', '%s', '%s', %s);" % (int(userid), type, sched, desc, float(amount))
    c.execute(query)
    db.commit()

try:
    insertExpense("43", "gym", "tamp fitness", "2020-09-19", "2.50")
    insertExpense("43", "gym", "tamp fitness", "2020-09-19", "2.50")
    insertIncome("43", "gym", "tamp fitness", "2020-09-19", "2.50")
    insertIncome("43", "gym", "tamp fitness", "2020-09-19", "2.50")
    insertRecurring("43", "+", "3", "membership", "2.50")
    insertRecurring("43", "-", "7", "salary", "3750")
except Exception as e:
    print("Unable to insert")
    print(e)
'''
INSERT INTO expenses (userid, category, description, created_dt, amount)
VALUES (123124, 'food', 'pizza hut', '2020-09-19', 2.1);
'''

'''
Adhoc
- Credit card
- Medical services
- Education
- Investment
- Charity
+ Bonus
+ Commission
+ Interest
+ Rebate
+ Refund

- Rent
- Subscriptions
- Bills
- Education
- Insurance
- Charity
- Tax (Road/Income/Property)
+ Income
+ 
'''