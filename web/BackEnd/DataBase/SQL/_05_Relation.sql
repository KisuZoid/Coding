CREATE TABLE orders (
    id NUMBER NOT NULL,
    order_number NUMBER,
    customer_id NUMBER, --will set as foreign key that points on particular record on customers table
    product_id NUMBER, --will set as foreign key that points on particular record on products table
    PRIMARY KEY (id),
    FOREIGN KEY (customer_id) REFERENCES customers(id), --here id is the primary key of customers table
    FOREIGN KEY (product_id) REFERENCES products(id) -- id is the primary key of products table
);
--primary key: id is primary key of order table. It uniquely identifies each record in the table
--foreign key is the key that links to the primary key of another table. It is used to establish the relationship between two tables.

INSERT INTO orders
VALUES (1, 4362, 2, 1);

INSERT INTO orders VALUES (2, 3254, 1, 1);
UPDATE orders SET product_id = 2 where id = 2;

--Join --> means combining rows from two or more tables based on a related column between them. It is used to combine data from two or more tables. 
SELECT orders.order_number, customers.customer_name, customers.age, products.product_name, products.price -- select the columns that you want to see order_number from orders table, name from customers table and name from products table
FROM orders --means that from the order table, we want to select all the records
INNER JOIN customers ON orders.customer_id = customers.id -- means that we are joining customers table with orders table on customer_id column
INNER JOIN products ON orders.product_id = products.id; --means that we are joining products table with orders table on product_id column. here 
-- inner join means that we will only see the records that have matching values in both tables. If there is no match, then the record will not be shown.
-- left join means that we will see all the records from the left table and the matching records from the right table . If there is no match, then the record will be shown with null values. --> similarly for right join, it means that we will see all the records from the right table and the matching records from the left table. If there is no match, then the record will be shown with null values.

--difference between inner join and join is that join is a keyword that is used to join two or more tables. It is used to combine rows from two or more tables based on a related column between them. Inner join is a type of join that is used to combine rows from two or more tables based on a related column between them. It is used to combine data from two or more tables. It only shows the records that have matching values in both tables. If there is no match, then the record will not be shown.

SELECT * FROM orders;