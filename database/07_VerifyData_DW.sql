USE ECommerceDW;
GO

SELECT 'DimCustomer' AS table_name, COUNT_BIG(*) AS row_count
FROM dw.DimCustomer

UNION ALL
SELECT 'DimProduct', COUNT_BIG(*) FROM dw.DimProduct

UNION ALL
SELECT 'DimDate', COUNT_BIG(*) FROM dw.DimDate

UNION ALL
SELECT 'FactSales', COUNT_BIG(*) FROM dw.FactSales;
GO

-- Total nilai penjualan per kategori produk
SELECT
p.Category,
SUM(f.Quantity) AS Total_Quantity,
SUM(f.SalesAmount) AS Total_Sales
FROM dw.FactSales AS f
JOIN dw.DimProduct AS p
ON f.ProductKey = p.ProductKey
GROUP BY p.Category
ORDER BY Total_Sales DESC;
GO

-- Ringkasan penjualan per bulan
SELECT
d.[Year],
d.[Month],
d.MonthName,
SUM(f.SalesAmount) AS Total_Sales,
COUNT(DISTINCT f.OrderID) AS Total_Orders
FROM dw.FactSales AS f
JOIN dw.DimDate AS d
ON f.DateKey = d.DateKey
GROUP BY d.[Year], d.[Month], d.MonthName
ORDER BY d.[Year], d.[Month];
GO