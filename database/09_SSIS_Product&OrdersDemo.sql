USE ECommerceStaging;
GO

IF OBJECT_ID(N'stg.SSIS_ProductsDemo', N'U') IS NULL
BEGIN
 CREATE TABLE stg.SSIS_ProductsDemo
 (
 Product_ID NVARCHAR(50) NULL,
 Product_Name NVARCHAR(200) NULL,
 Category NVARCHAR(100) NULL,
 Unit_Price NVARCHAR(50) NULL
 );
END;
GO

IF OBJECT_ID(N'stg.SSIS_OrdersDemo', N'U') IS NULL
BEGIN
 CREATE TABLE stg.SSIS_OrdersDemo
 (
 Order_ID NVARCHAR(50) NULL,
 Customer_ID NVARCHAR(50) NULL,
 Order_Date NVARCHAR(50) NULL,
 Order_Status NVARCHAR(50) NULL
 );
END;
GO