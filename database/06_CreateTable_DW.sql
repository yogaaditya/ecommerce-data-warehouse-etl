USE ECommerceDW;
GO

-- Dimensi customer
IF OBJECT_ID(N'dw.DimCustomer', N'U') IS NULL
BEGIN
 CREATE TABLE dw.DimCustomer (
 CustomerKey INT IDENTITY(1,1) NOT NULL
 CONSTRAINT PK_DimCustomer PRIMARY KEY,
 CustomerID NVARCHAR(100) NOT NULL,
 CustomerName NVARCHAR(200) NOT NULL,
 Email NVARCHAR(200) NULL,
 City NVARCHAR(100) NULL,
 SignupDate DATE NULL,
 CONSTRAINT UQ_DimCustomer_CustomerID
 UNIQUE (CustomerID)
 );
END;
GO

-- Dimensi produk
IF OBJECT_ID(N'dw.DimProduct', N'U') IS NULL
BEGIN
 CREATE TABLE dw.DimProduct (
 ProductKey INT IDENTITY(1,1) NOT NULL
 CONSTRAINT PK_DimProduct PRIMARY KEY,
 ProductID NVARCHAR(100) NOT NULL,
 ProductName NVARCHAR(200) NOT NULL,
 Category NVARCHAR(100) NULL,
 UnitPrice DECIMAL(18,2) NOT NULL,
 CONSTRAINT UQ_DimProduct_ProductID
 UNIQUE (ProductID)
 );
END;
GO

-- Dimensi tanggal
IF OBJECT_ID(N'dw.DimDate', N'U') IS NULL
BEGIN
 CREATE TABLE dw.DimDate (
 DateKey INT NOT NULL
 CONSTRAINT PK_DimDate PRIMARY KEY,
 FullDate DATE NOT NULL
 CONSTRAINT UQ_DimDate_FullDate UNIQUE,
 [Year] SMALLINT NOT NULL,
 [Quarter] TINYINT NOT NULL,
 [Month] TINYINT NOT NULL,
 MonthName NVARCHAR(20) NOT NULL,
 [Day] TINYINT NOT NULL
 );
END;
GO

-- Tabel fakta penjualan
IF OBJECT_ID(N'dw.FactSales', N'U') IS NULL
BEGIN
 CREATE TABLE dw.FactSales (
 SalesKey BIGINT IDENTITY(1,1) NOT NULL
 CONSTRAINT PK_FactSales PRIMARY KEY,
 OrderItemID NVARCHAR(100) NOT NULL,
 OrderID NVARCHAR(100) NOT NULL,
 CustomerKey INT NOT NULL,
 ProductKey INT NOT NULL,
 DateKey INT NOT NULL,
 OrderStatus NVARCHAR(100) NOT NULL,
 Quantity INT NOT NULL,
 UnitPrice DECIMAL(18,2) NOT NULL,
 SalesAmount DECIMAL(18,2) NOT NULL,
 LoadDate DATETIME2 NOT NULL
 CONSTRAINT DF_FactSales_LoadDate
 DEFAULT SYSDATETIME(),

 CONSTRAINT UQ_FactSales_OrderItemID
 UNIQUE (OrderItemID),

 CONSTRAINT FK_FactSales_Customer
 FOREIGN KEY (CustomerKey)
 REFERENCES dw.DimCustomer(CustomerKey),

 CONSTRAINT FK_FactSales_Product
 FOREIGN KEY (ProductKey)
 REFERENCES dw.DimProduct(ProductKey),

 CONSTRAINT FK_FactSales_Date
 FOREIGN KEY (DateKey)
 REFERENCES dw.DimDate(DateKey),

 CONSTRAINT CK_FactSales_Quantity
 CHECK (Quantity > 0),

 CONSTRAINT CK_FactSales_SalesAmount
 CHECK (SalesAmount >= 0)
 );
END;
GO