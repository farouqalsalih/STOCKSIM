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
        return False

    if buy:
        execute_buy_order(user_id, cursor.lastrowid, ticker, shares, price)
    else:
        execute_sell_order(user_id, cursor.lastrowid, ticker, shares, price)
    return True

def execute_buy_order(user_id, order_id, ticker, shares, price):
    connection = get_database_connection()
    cursor = connection.cursor()

    # Fetch available sell orders for the requested asset
    cursor.execute("""
        SELECT order_id, user_id, shares, price, executed
        FROM ORDERS
        WHERE ticker = %s AND buy = 0 AND price <= %s AND shares > 0
        ORDER BY price ASC, order_date ASC
    """, (ticker, price))

    sell_orders = cursor.fetchall()

    # Loop through the sell orders and execute the trades
    for sell_order_id, sell_user_id, sell_shares, sell_price, sell_executed in sell_orders:
        if shares == 0:
            break

        # Determine the number of shares to execute in the current trade
        executed_shares = min(shares, sell_shares - sell_executed)

        # Update the buy order's remaining shares
        shares -= executed_shares

        # Update the buyer and sell order's remaining shares in the database
        cursor.execute("""
            UPDATE ORDERS
            SET executed = executed + %s
            WHERE order_id = %s
        """, (executed_shares, sell_order_id))

        cursor.execute(
            """
            UPDATE ORDERS
            SET executed = executed + %s
            WHERE order_id = %s
        """, (executed_shares, order_id))

        # Calculate the trade amount
        trade_amount = executed_shares * sell_price

        # Update the seller's cash balances in the database
        cursor.execute("""
            UPDATE USERS
            SET cash = cash + %s
            WHERE user_id = %s
        """, (trade_amount, sell_user_id))

        # Update the buyer's portfolio
        cursor.execute("""
            INSERT INTO PORTFOLIOS (user_id, ticker, shares)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE shares = shares + %s
        """, (user_id, ticker, executed_shares, executed_shares))

    # Commit the changes to the database
    connection.commit()

    cursor.close()
    connection.close()

def execute_sell_order(user_id, order_id, ticker, shares, price):
