--read all --> use *
-- SELECT * FROM table_name;

--read particular value
-- SELECT column_name(s) FROM table_name;

SELECT name FROM products;--gives the name of all products
SELECT * FROM products; --gives the name, price, and quantity of all products

--read a particular row
-- SELECT column_name FROM table_name WHERE condition;
SELECT * FROM products
WHERE id = 1; --give the product with id 1