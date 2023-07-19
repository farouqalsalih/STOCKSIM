import mysql.connector
import datetime
import random

mydb = mysql.connector.connect(
        host='host',
        database = 'stocksim',
        user='root',
        password='password',
        autocommit = False
        )
cursor = mydb.cursor()

def initStock(name, p, a):
    X = 1000
    start_date = datetime.date(2023, 4, 8)
    end_date = datetime.date(3023, 4, 8)
    delta = datetime.timedelta(days=1)
    while (start_date <= end_date):
        coin_flip = random.random()        
        if coin_flip <= p:
            increase = random.uniform(0,X)
            portion = random.uniform(0.0, a)
            X = X + increase*(1.0-portion)                        
            cursor.execute("INSERT INTO DIVIDENDS (payment_date, payout, ticker) VALUES ('" + str(start_date) + "', " + str(increase*portion) + ", '" + name + "');")
        else:
            X = X - random.uniform(0, X*0.5)            
            cursor.execute("INSERT INTO DIVIDENDS (payment_date, payout, ticker) VALUES ('" + str(start_date) + "', 0.0, '" + name + "');")                                  
        start_date += delta 

def signUp(user_id, email, first, last, phone, cash):    
    cursor.execute("INSERT INTO USERS (user_id, email, first_name, last_name, cash, phone_number) VALUES (" + str(user_id) + ", '" + email + "', '" + first + "', '" + last + "', " + str(cash) + ", '"+ phone+"');")
    if first == "ADMIN":
        giveUserStock(user_id, "AZ", 10)
        giveUserStock(user_id, "BT", 10)
        giveUserStock(user_id, "CTC", 10)
        giveUserStock(user_id, "DHT", 10)
        giveUserStock(user_id, "EFG", 10)
        giveUserStock(user_id, "GIJ", 10)
        giveUserStock(user_id, "FLJ", 10)
        giveUserStock(user_id, "DEI", 10)
        giveUserStock(user_id, "FLK", 10)
        giveUserStock(user_id, "DXI", 10) 
def giveUserStock(user_id, ticker, shares):    
    cursor.execute("SELECT * FROM PORTFOLIOS WHERE PORTFOLIOS.user_id = " + str(user_id) + " and PORTFOLIOS.ticker = '" + ticker+"'")        
    if cursor.fetchone() == None:
        cursor.reset()
        cursor.execute("INSERT INTO PORTFOLIOS (user_id, ticker, shares) VALUES (" + str(user_id) + ", '" + ticker + "', " + str(shares) + ");")
    else:
        cursor.execute("UPDATE PORTFOLIOS SET PORTFOLIOS.shares = PORTFOLIOS.shares + " + str(shares) + " WHERE PORTFOLIOS.user_id = " + str(user_id) + " and PORTFOLIOS.ticker = '" + str(ticker)+"'")
        
def placeOrder(order_id, user_id, ticker, buying, shares, price):
    if buying:
        cursor.execute("SELECT SUM(price) FROM ORDERS WHERE ORDERS.buy = TRUE and ORDERS.user_id = " + str(user_id))
        tempUnavailable = cursor.fetchone()
        unavailableMoney = price
        if tempUnavailable != None and tempUnavailable[0] != None:
            unavailableMoney += tempUnavailable[0]             
        cursor.execute("SELECT cash FROM USERS WHERE USERS.user_id = " + str(user_id))
        availableMoney = cursor.fetchone()[0]
        if  availableMoney - unavailableMoney >= 0:        
            cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = FALSE and ORDERS.executed= FALSE and ORDERS.price <= " + str(price) + " and ORDERS.shares = " + str(shares) + " and ORDERS.ticker = '" + str(ticker)+"'")            
            if cursor.fetchone() == None:                
                cursor.reset()
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', TRUE, " + str(shares) + ", " + str(price) + ", FALSE);")
            else:                
                cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = FALSE and ORDERS.executed= FALSE and ORDERS.price = (SELECT MIN(price) FROM ORDERS) and ORDERS.shares = '" + str(shares) + "' and ORDERS.ticker = '" + str(ticker)+"'")
                cheapestSeller = cursor.fetchone()                
                updateCash(user_id, (-1)*cheapestSeller[5])
                giveUserStock(user_id, ticker, shares)
                giveUserStock(cheapestSeller[1], ticker, (-1)*shares)
                updateCash(cheapestSeller[1], cheapestSeller[5])
                cursor.execute("UPDATE ORDERS SET ORDERS.executed = TRUE WHERE ORDERS.order_id = " + str(cheapestSeller[0]))
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', True, " + str(shares) + ", " + str(price) + ", TRUE);")
    else:
        cursor.execute("SELECT SUM(shares) FROM ORDERS WHERE ORDERS.buy = FALSE and ORDERS.ticker = '" + ticker + "' and ORDERS.user_id = " + str(user_id))
        tempUnavShares = cursor.fetchone()
        unavailableShares = shares 
        if tempUnavShares != None and tempUnavShares[0] != None:
            unavailableShares += tempUnavShares[0]        
        cursor.execute("SELECT SUM(shares) FROM PORTFOLIOS WHERE PORTFOLIOS.ticker = '" + ticker + "' and PORTFOLIOS.user_id = " + str(user_id))
        tempTotal = cursor.fetchone()
        totalShares = 0
        if tempTotal != None and tempTotal[0] != None:
            totalShares = tempTotal[0]       
        if  totalShares - unavailableShares >= 0:
            cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = TRUE and ORDERS.executed = FALSE and ORDERS.price >= " + str(price) + " and ORDERS.shares = " + str(shares) + " and ORDERS.ticker = '" + ticker+"'")            
            if cursor.fetchone() == None:
                cursor.reset()
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', FALSE, " + str(shares) + ", " + str(price) + ", FALSE);")
            else:               
                cursor.execute("SELECT * FROM ORDERS WHERE ORDERS.buy = TRUE and ORDERS.executed = FALSE and ORDERS.price = (SELECT MAX(price) FROM ORDERS) and ORDERS.shares = " + str(shares) + " and ORDERS.ticker = '" + str(ticker) + "'")
                mostExpensiveBuyer = cursor.fetchone()
                updateCash(mostExpensiveBuyer[1], (-1)*mostExpensiveBuyer[5])
                updateCash(user_id, mostExpensiveBuyer[5])
                giveUserStock(mostExpensiveBuyer[1], ticker, shares)
                giveUserStock(user_id, ticker, (-1)*shares)
                cursor.execute("UPDATE ORDERS SET ORDERS.executed = TRUE WHERE ORDERS.order_id = " + str(mostExpensiveBuyer[0]))
                cursor.execute("INSERT INTO ORDERS (order_id, user_id, ticker, buy, shares, price, executed) VALUES (" + str(order_id) + ", " + str(user_id) + ", '" + ticker + "', FALSE, " + str(shares) + ", " + str(price) + ", TRUE);")
                            
def updateCash(user_id, ammount):
    cursor.execute("UPDATE USERS SET USERS.cash = USERS.cash + " + str(ammount) + "WHERE USERS.user_id = '" + str(user_id) + "'")
signUp(2, 'fake@fake.com', "John1", "Doe1", "911", 100.0)
signUp(1, 'fak2e@fake.com', "John", "Doe2", "9221", 1000.0)
print("users have signed up and user 2 has $100 and user 1 has $1000")
cursor.execute("SELECT * FROM USERS;")
for x in cursor:
    print(x)
initStock("A", 0.45, 0.1)
print("stock A has been created")




giveUserStock(2, 'A', 5)
print("USER 2 has 5 shares of stock A")
cursor.execute("SELECT * FROM PORTFOLIOS;")
for x in cursor:
    print(x)
placeOrder(2,1, "A", True, 1, 4)
print("The buy order has been placed")
placeOrder(1, 2, "A", False, 500, 100)
print("The sell order has been placed")



cursor.execute("SELECT * FROM ORDERS")
for x in cursor:
    print(x)


print("We want to see that User 2 has 0 shares of A and 1000 in cash and User 1 has 5 shares of A and $100")

cursor.execute("SELECT * FROM USERS;")
for x in cursor:
    print(x)

    

cursor.execute("SELECT * FROM PORTFOLIOS;")
for x in cursor:
    print(x)

print("HERE ARE THE CURRENT ORDERS:")
cursor.execute("SELECT * FROM ORDERS;")
for x in cursor:
    print(x)
cursor.close()
mydb.close()

    


    
