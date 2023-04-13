def giveDividends():
    today = datetime.date.today()
    cursor.execute("SELECT user_id FROM USERS")

    user_id_list = cursor.fetchall()

    for user_id in user_id_list:
        cursor.execute("SELECT ticker, shares FROM PORTFOLIOS WHERE PORTFOLIOS.user_id = " + str(user_id[0]))

        ticker_shares = cursor.fetchall()

        for tup in ticker_shares:
            ticker, shares = tup

            cursor.execute("SELECT payout FROM DIVIDENDS WHERE DIVIDENDS.ticker = '" + ticker + "' AND payment_date = '" + str(today) + "'")
            payout = cursor.fetchone()[0]
           

            updateCash(user_id[0], payout*shares)
