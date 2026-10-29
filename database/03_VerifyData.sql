USE ECommerceStaging;
GO

SELECT 'Customers' AS table_name, COUNT_BIG(*) AS row_count
FROM stg.Customers

UNION ALL
SELECT 'Products', COUNT_BIG(*) FROM stg.Products

UNION ALL
SELECT 'Orders', COUNT_BIG(*) FROM stg.Orders

UNION ALL
SELECT 'OrderItems', COUNT_BIG(*) FROM stg.OrderItems

UNION ALL
SELECT 'Payments', COUNT_BIG(*) FROM stg.Payments

UNION ALL
SELECT 'Shipments', COUNT_BIG(*) FROM stg.Shipments;
GO