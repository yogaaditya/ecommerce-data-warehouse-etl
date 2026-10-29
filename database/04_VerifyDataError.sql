USE ECommerceStaging;
GO

-- Duplikasi order
SELECT order_id, COUNT(*) AS jumlah
FROM stg.Orders
GROUP BY order_id
HAVING COUNT(*) > 1;
GO

-- Quantity nol atau negatif
SELECT *
FROM stg.OrderItems
WHERE TRY_CONVERT(INT, quantity) IS NULL
OR TRY_CONVERT(INT, quantity) <= 0;
GO

-- Product ID yang tidak ada di master produk
SELECT oi.*
FROM stg.OrderItems AS oi
LEFT JOIN stg.Products AS p
ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;
GO

-- Email customer kosong
SELECT *
FROM stg.Customers
WHERE NULLIF(LTRIM(RTRIM(email)), '') IS NULL;
GO

-- Duplikasi order item
SELECT order_item_id,order_id, COUNT(*) AS JUMLAH
FROM stg.OrderItems
GROUP BY order_item_id, order_id
HAVING COUNT(*) > 1;
GO