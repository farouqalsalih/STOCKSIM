import mysql.connector

def signUp(user_id, email, first, last, phone, cash, password, cursor):    
    cursor.execute("INSERT IGNORE INTO USERS (user_id, email, first_name, last_name, cash, phone_number, user_password) VALUES (" + str(user_id) + ", '" + email + "', '" + first + "', '" + last + "', " + str(cash) + ", '"+ phone+"', '"+password+ "');")

def validate(user_id, password, cursor):
    cursor.execute("SELECT * FROM USERS WHERE USERS.user_id = " + str(user_id) + " and USERS.user_password = '" + password + "'")
    return cursor.fetchone()

    