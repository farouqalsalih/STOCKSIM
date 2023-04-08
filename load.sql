CREATE TABLE USER (
    user_id INT NOT NULL,
    email VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL, 
    phone_number VARCHAR(20) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE DIVIDEND (
    ticker VARCHAR(50) NOT NULL,
    payout FLOAT(0) NOT NULL,
    payment_date DATE NOT NULL, 
    PRIMARY KEY (ticker)
);

CREATE TABLE MARKET (
    order_id INT NOT NULL, 
    quantity_executed INT NOT NULL,
    ticker VARCHAR(50) NOT NULL, 
    buy BOOL NOT NULL, 
    shares INT NOT NULL, 
    price FLOAT(0) NOT NULL, 
    PRIMARY KEY (order_id),
    FOREIGN KEY (ticker) REFERENCES DIVIDEND(ticker)
)