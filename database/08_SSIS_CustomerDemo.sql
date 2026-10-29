USE ECommerceStaging;
GO

IF OBJECT_ID(N'stg.SSIS_CustomersDemo', N'U') IS NULL
BEGIN
 CREATE TABLE stg.SSIS_CustomersDemo
 (
 Customer_ID NVARCHAR(50) NULL,
 Customers_Name NVARCHAR(100) NULL,
 Email NVARCHAR(255) NULL,
 City NVARCHAR(100) NULL,
 Signup_Date NVARCHAR(100) NULL
 );
END;
GO

select table_schema,
table_name
from information_Schema.tables
where table_name = 'SSIS_CustomersDemo';

select * from stg.SSIS_CustomersDemo;

select count(*) AS TOTAL
from stg.SSIS_CustomersDemo;