--Create Table:
-- CREATE TABLE table_name(
--     column1 data_type,
--     column2 data_type
-- );
-- DataType parameter specifies the type of data the column can hold (eg. varchar, integer, data etc)

-- this is schema that indicates the structure of the database
CREATE TABLE products(
    id NUMBER NOT NULL, -- Unique identifier for each product due to primary key, and not null indicates it cannot be empty.
    name VARCHAR(200), -- name of the product, it can hold up to 200 characters.
    price NUMBER(10, 2), -- price of the product, it can hold up to 10 digits with 2 decimal places.
    PRIMARY KEY (id) -- this is the primary key that uniquely identifies each row in the table.
);

--insert data into the table both column and values
-- INSERT INTO table_name(column1, column2, ...) 
-- VALUES (value1, value2, ...);

--insert data into the table where we add values for all the columns in the table
-- INSERT INTO table_name
-- VALUES (value1, value2, ...);

INSERT into products
VALUES (1, 'Pen', 1.20);

INSERT INTO products(id, name)
VALUES (2, 'Pencil'); -- we can insert values for specific columns

INSERT into products
VALUES (3, 'Pencil', 0.50);


--ALTER the name of culumn
ALTER TABLE products RENAME COLUMN name TO product_name;
SELECT * FROM products; -- this will return all (*) the rows from product in the table.