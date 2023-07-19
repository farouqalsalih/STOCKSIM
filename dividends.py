import mysql.connector
import datetime
import random

## make the DB yours and run  this to initialize Dividends 

mydb = mysql.connector.connect(
        host='host',
        database = 'stocksim',
        user='root',
        password='password',
        autocommit = False
        )
cursor = mydb.cursor()

def initStock(name, p, a):
    X = random.uniform(1,1000)
    start_date = datetime.date(2021, 4, 8)
    end_date = datetime.date(2025, 4, 8)
    delta = datetime.timedelta(days=1)
    while (start_date <= end_date):
        coin_flip = random.random()        
        if coin_flip <= p:
            increase = random.uniform(0,X)
            portion = random.uniform(a*0.2, a)
            payout = max(min(increase*portion, 10.0**38), 10.0**(-38))
            X = X + increase - payout
            

            
            cursor.execute("INSERT INTO DIVIDENDS (payment_date, payout, ticker) VALUES ('" + str(start_date) + "', " + str(payout) + ", '" + name + "');")
        else:
            X = X - random.uniform(0, X*0.5)            
            cursor.execute("INSERT INTO DIVIDENDS (payment_date, payout, ticker) VALUES ('" + str(start_date) + "', 0.0, '" + name + "');")                                  
        start_date += delta

initStock("AZ", 0.45, 0.1)
initStock("BT", 0.6, 0.5)
initStock("CTC", 0.7, 0.01)
initStock("DHT", 0.4, 0.8)
initStock("EFG", 0.5, 0.5)
initStock("GIJ", 0.4, 0.8)
initStock("FLJ", 0.4, 0.8)
initStock("DEI", 0.4, 0.8)
initStock("FLK", 0.9, 0.01)
initStock("DXI", 0.5, 0.3)
cursor.execute("SELECT * FROM DIVIDENDS")
for x in cursor:
    print(x)



