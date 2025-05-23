--Delete
-- DELETE FROM table_name WHERE condition;
DELETE FROM products --WHERE statement is necessary else it will delete all the rows in the table.
WHERE name = 'Pencil'; --it will delete all rows where name is pencil


INSERT INTO products 
VALUES (2, 'Pencil', 10.00, 100); --inserting a new row into the table. The values

SELECT * FROM products; 