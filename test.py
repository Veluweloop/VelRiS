# import pymysql.connector
import pymysql.cursors

mydb = pymysql.connect(
    host= "srv962.hstgr.io",
    user= "u328463558_VELUWELOOP_TST",
    password= "VeluweloopTijd1!"
)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)