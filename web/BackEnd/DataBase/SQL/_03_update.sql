--Update
-- UPDATE table_name SET column1 = value1, column2 = value2 WHERE condition;
UPDATE products
SET price = 0.8 --where statement is needed else it will update all rows
WHERE id = 2;

--Alter table
-- ALTER TABLE table_name ADD COLUMN new_column data_type;
ALTER TABLE products
ADD stock NUMBER; --add a new column named stock with data type number

UPDATE products
SET stock = 32
WHERE id = 2;

SELECT * FROM products;