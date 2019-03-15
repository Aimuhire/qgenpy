import mysql.connector

try:
    myDB = mysql.connector.connect(
        host="localhost",
        user="mars",
        passwd="dGHSN8u3**9(99009$%$%%%mysql",
        database="qpydb",
    )
except Exception as e:
    raise
    print("Failed to connect to db", e)

myCursor = myDB.cursor()
try:
    myCursor.execute("CREATE DATABASE qpydb")
except:
    pass
myCursor.execute("SHOW DATABASES")
for db in myCursor:
    print(db)

myCursor.execute(
    "CREATE TABLE quotes (quote VARCHAR(500),author VARCHAR(255),category VARCHAR(255),tags VARCHAR(255))"
)

insertQuoteSqlFormula="INSERT INTO quotes (quote,autor,category,tags) values(%s,%s,%s,%s)"

myCursor.execute(insertQuoteSqlFormula,"quote")