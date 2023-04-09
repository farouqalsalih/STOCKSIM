CREATE TABLE USERS (
    user_id INT NOT NULL,
    email VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL, 
    cash float(0) NOT NULL, 
    phone_number VARCHAR(20) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE DIVIDENDS (
    ticker VARCHAR(50) NOT NULL,
    payout FLOAT(0) NOT NULL,
    payment_date DATE NOT NULL, 
    PRIMARY KEY (ticker, payment_date)
);

CREATE TABLE ORDERS (
    order_id INT NOT NULL, 
    user_id INT NOT NULL,
    ticker VARCHAR(50) NOT NULL, 
    buy BOOL NOT NULL, 
    shares INT NOT NULL, 
    price FLOAT(0) NOT NULL, 
    executed BOOL NOT NULL,
    PRIMARY KEY (order_id),
    FOREIGN KEY (ticker) REFERENCES DIVIDENDS(ticker),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE STATS (
    user_id INT NOT NULL, 
    instance_date DATE NOT NULL,
    user_rank INT NOT NULL, 
    total_users INT NOT NULL,
    portfolio_value FLOAT(0) NOT NULL,
    PRIMARY KEY (user_id, instance_date),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id)
);

CREATE TABLE PORTFOLIOS (
    user_id INT NOT NULL, 
    ticker VARCHAR(50) NOT NULL, 
    shares INT NOT NULL,
    PRIMARY KEY (user_id, ticker),
    FOREIGN KEY (user_id) REFERENCES USERS(user_id),
    FOREIGN KEY (ticker) REFERENCES DIVIDENDS(ticker)
);