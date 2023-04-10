CREATE TABLE USERS (
    user_id INT NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL, 
    cash float(0) NOT NULL, 
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    user_password VARCHAR(20) NOT NULL,
    PRIMARY KEY (user_id)
);

CREATE TABLE DIVIDENDS (
    ticker VARCHAR(50) NOT NULL,
    payout FLOAT(0) NOT NULL,
    payment_date DATE NOT NULL, 
    PRIMARY KEY (ticker, payment_date)
);

CREATE TABLE ORDERS (
    order_id INT AUTO_INCREMENT NOT NULL, 
    user_id INT NOT NULL,
    ticker VARCHAR(50) NOT NULL, 
    buy BOOL NOT NULL, 
    shares INT NOT NULL, 
    price FLOAT(0) NOT NULL, 
    executed INT NOT NULL,
    order_date DATETIME NOT NULL CURRENT_TIMESTAMP,
    cancelled BOOL NOT NULL,
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


DELIMITER //
CREATE TRIGGER check_and_update_funds_and_assets_before_order
BEFORE INSERT ON ORDERS
FOR EACH ROW
BEGIN
    IF NEW.shares <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Shares value must be greater than 0.';
    END IF;

    IF NEW.price < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: Price value must be equal to or greater than 0.';
    END IF;

    IF NEW.buy = 1 THEN
        DECLARE user_cash FLOAT;
        SELECT cash INTO user_cash FROM USERS WHERE user_id = NEW.user_id;

        IF user_cash < (NEW.shares * NEW.price) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient funds for buy order';
        ELSE
            UPDATE USERS
            SET cash = cash - (NEW.shares * NEW.price)
            WHERE user_id = NEW.user_id;
        END IF;
    ELSEIF NEW.buy = 0 THEN
        DECLARE user_shares INT;
        SELECT shares INTO user_shares FROM PORTFOLIOS WHERE user_id = NEW.user_id AND ticker = NEW.ticker;

        IF user_shares < NEW.shares THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient assets for sell order';
        ELSE
            UPDATE PORTFOLIOS
            SET shares = shares - NEW.shares
            WHERE user_id = NEW.user_id AND ticker = NEW.ticker;
        END IF;
    END IF;
END;
//
DELIMITER ;


DELIMITER //
CREATE TRIGGER remove_zero_shares_after_update
AFTER UPDATE ON PORTFOLIOS
FOR EACH ROW
BEGIN
    IF NEW.shares = 0 THEN
        DELETE FROM PORTFOLIOS WHERE user_id = NEW.user_id AND ticker = NEW.ticker;
    END IF;
END;
//
DELIMITER ;
