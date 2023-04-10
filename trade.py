import mysql.connector

def get_database_connection():
    return mysql.connector.connect(
        host='Farouqs-MacBook-Air.local',
        database='stocksim',
        user='root',
        password='your_password',
        autocommit=False
    )

def signUp(user_id, email, first, last, cash, phone, user_password):
    connection = get_database_connection()
    cursor = connection.cursor()
    success

    try:
        cursor.execute(f"INSERT INTO USERS (user_id, email, first_name, last_name, cash, phone_number, user_password) VALUES ({str(user_id)}, '{email}', '{first}', '{last}', {str(cash)}, '{phone}', '{user_password}');")
        connection.commit()
        success = False
    except mysql.connector.Error as e:
        print(f"Error: {e}")
        success = True
    finally:
        cursor.close()
        connection.close()
        return success

def createOrder(user_id, ticker, buy, shares, price):
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                INSERT INTO ORDERS (user_id, ticker, buy, shares, price, executed)
                VALUES (%s, %s, %s, %s, %s, 0)
            """, (user_id, ticker, buy, shares, price))

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        return

    if buy:
        execute_buy_order(user_id, cursor.lastrowid, ticker, shares, price)
    else:
        execute_sell_order(user_id, cursor.lastrowid, ticker, shares, price)

def execute_buy_order(user_id, order_id, ticker, shares, price):
    return

def execute_sell_order(user_id, order_id, ticker, shares, price):
