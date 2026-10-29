USE ECommerceStaging;
GO

CREATE TABLE stg.Customers (
customer_id NVARCHAR(100),
customer_name NVARCHAR(200),
email NVARCHAR(200),
city NVARCHAR(100),
signup_date NVARCHAR(50)
);
GO

CREATE TABLE stg.Products (
product_id NVARCHAR(100),
product_name NVARCHAR(200),
category NVARCHAR(100),
unit_price NVARCHAR(50)
);
GO

CREATE TABLE stg.Orders (
order_id NVARCHAR(100),
customer_id NVARCHAR(100),
order_date NVARCHAR(50),
order_status NVARCHAR(100)
);
GO

CREATE TABLE stg.OrderItems (
order_item_id NVARCHAR(100),
order_id NVARCHAR(100),
product_id NVARCHAR(100),
quantity NVARCHAR(50),
unit_price NVARCHAR(50)
);
GO

CREATE TABLE stg.Payments (
payment_id NVARCHAR(100),
order_id NVARCHAR(100),
payment_method NVARCHAR(100),
payment_status NVARCHAR(100),
payment_date NVARCHAR(50)
);
GO

CREATE TABLE stg.Shipments (
shipment_id NVARCHAR(100),
order_id NVARCHAR(100),
shipment_status NVARCHAR(100),
shipped_date NVARCHAR(50),
delivered_date NVARCHAR(50)
);
GO