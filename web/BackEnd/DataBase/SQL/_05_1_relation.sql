CREATE TABLE customers(
    id NUMBER PRIMARY KEY
);

ALTER TABLE customers 
ADD name VARCHAR(100);

ALTER TABLE customers
ADD age NUMBER;

-- ALTER the name of column of the table
ALTER TABLE customers RENAME COLUMN name to customer_name;

INSERT INTO customers (id) VALUES (1);
INSERT INTO customers (id) VALUES (2);
UPDATE customers SET name = 'John' WHERE id = 1;
UPDATE customers SET name = 'Doe' WHERE id = 2;
UPDATE customers SET age = 5 WHERE id = 2;
UPDATE customers SET age = 6 WHERE id = 1;



INSERT INTO customers VALUES (3, 'John Doe', 30);

SELECT * FROM customers;