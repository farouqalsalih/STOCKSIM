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

def cancel_order(user_id, order_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    # Fetch order information
    cursor.execute("""
        SELECT ticker, shares, price, executed, buy, cancelled
        FROM ORDERS
        WHERE order_id = %s AND user_id = %s
    """, (order_id, user_id))

    order = cursor.fetchone()

    if not order:
        print("Error: Order not found.")
        return

    ticker, shares, price, executed, buy, cancelled = order

    if not buy:
        print("Error: This is not a buy order.")
        return

    if cancelled:
        print("Error: The order is already cancelled.")
        return

    # Calculate the remaining cash for the unexecuted shares
    remaining_shares = shares - executed
    refund_amount = remaining_shares * price

    # Update the order status to cancelled
    cursor.execute("""
        UPDATE ORDERS
        SET cancelled = 1
        WHERE order_id = %s
    """, (order_id,))

    # Refund the cash amount back to the user
    cursor.execute("""
        UPDATE USERS
        SET cash = cash + %s
        WHERE user_id = %s
    """, (refund_amount, user_id))

    # Commit the changes to the database
    connection.commit()

    cursor.close()
    connection.close()
    print(f"Buy order {order_id} has been cancelled successfully.")


def createOrder(user_id, ticker, buy, shares, price):
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
                INSERT INTO ORDERS (user_id, ticker, buy, shares, price, executed, cancelled)
                VALUES (%s, %s, %s, %s, %s, 0, 0)
            """, (user_id, ticker, buy, shares, price))

    except mysql.connector.Error as e:
        print(f"Error: {e}")
        cursor.close()
        connection.close()
        return False

    if buy:
        execute_buy_order(user_id, cursor.lastrowid, ticker, shares, price)
    else:
        execute_sell_order(user_id, cursor.lastrowid, ticker, shares, price)
    
    connection.commit()

    cursor.close()
    connection.close()
    return True

def execute_buy_order(user_id, order_id, ticker, shares, price):
    connection = get_database_connection()
    cursor = connection.cursor()

    # Fetch available sell orders for the requested asset
    cursor.execute("""
        SELECT order_id, user_id, shares, price, executed
        FROM ORDERS
        WHERE ticker = %s AND buy = 0 AND price <= %s AND executed < shares AND cancelled = 0
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
    connection = get_database_connection()
    cursor = connection.cursor()

    # Fetch available buy orders for the requested asset
    cursor.execute("""
        SELECT order_id, user_id, shares, price, executed
        FROM ORDERS
        WHERE ticker = %s AND buy = 1 AND price >= %s AND executed < shares AND cancelled = 0
        ORDER BY price DESC, order_date ASC
    """, (ticker, price))

    buy_orders = cursor.fetchall()

    # Loop through the buy orders and execute the trades
    for buy_order_id, buy_user_id, buy_shares, buy_price, buy_executed in buy_orders:
        if shares == 0:
            break

        # Determine the number of shares to execute in the current trade
        executed_shares = min(shares, buy_shares - buy_executed)

        # Update the sell order's remaining shares
        shares -= executed_shares

        # Update the buyer and sell order's remaining shares in the database
        cursor.execute("""
            UPDATE ORDERS
            SET executed = executed + %s
            WHERE order_id = %s
        """, (executed_shares, buy_order_id))

        cursor.execute(
            """
            UPDATE ORDERS
            SET executed = executed + %s
            WHERE order_id = %s
        """, (executed_shares, order_id))

        # Calculate the trade amount
        trade_amount = executed_shares * buy_price

        # Update the seller's cash balances and portfolio in the database
        cursor.execute("""
            UPDATE USERS
            SET cash = cash + %s
            WHERE user_id = %s
        """, (trade_amount, user_id))

        # Update the buyer's portfolio
        cursor.execute("""
            INSERT INTO PORTFOLIOS (user_id, ticker, shares)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE shares = shares + %s
        """, (buy_user_id, ticker, executed_shares, executed_shares))

    # Commit the changes to the database
    connection.commit()

    cursor.close()
    connection.close()
