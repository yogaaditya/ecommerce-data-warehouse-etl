
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pyodbc


# ============================================================
# KONFIGURASI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

SERVER = "localhost"
DRIVER = "ODBC Driver 18 for SQL Server"

STAGING_DB = "ECommerceStaging"
WAREHOUSE_DB = "ECommerceDW"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={STAGING_DB};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def parse_date(value):
    value = str(value).strip()
    if not value:
        return None
    return date.fromisoformat(value)


def parse_decimal(value):
    return Decimal(str(value).strip())


def fetch_all(cursor, sql):
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def main():
    print("=" * 60)
    print("ETL: STAGING -> DATA WAREHOUSE")
    print("=" * 60)

# Koneksi staging untuk membaca sumber.
    source_connection = pyodbc.connect(CONNECTION_STRING)

    try:
        source_cursor = source_connection.cursor()

        customers = fetch_all(
            source_cursor,
            """
            SELECT customer_id, customer_name, email,
            city, signup_date
            FROM stg.Customers
            """,
        )

        products = fetch_all(
            source_cursor,
            """
            SELECT product_id, product_name, category, unit_price
            FROM stg.Products
            """,
        )

        orders = fetch_all(
            source_cursor,
            """
            SELECT order_id, customer_id, order_date, order_status
            FROM stg.Orders
            ORDER BY order_id
            """,
        )

        order_items = fetch_all(
            source_cursor,
            """
            SELECT order_item_id, order_id, product_id,
            quantity, unit_price
            FROM stg.OrderItems
            ORDER BY order_item_id
            """,
        )

        source_cursor.close()

    finally:
        source_connection.close()

# Koneksi langsung ke database warehouse.
    warehouse_connection_string = (
        f"DRIVER={{{DRIVER}}};"
        f"SERVER={SERVER};"
        f"DATABASE={WAREHOUSE_DB};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    connection = pyodbc.connect(
        warehouse_connection_string,
        autocommit=False,
    )

    try:
        cursor = connection.cursor()

# Pastikan proses dijalankan ulang tanpa menambah
# data duplikat. Hapus fakta terlebih dahulu agar
# foreign key tidak terlanggar.
        cursor.execute("DELETE FROM dw.FactSales")
        cursor.execute("DELETE FROM dw.DimDate")
        cursor.execute("DELETE FROM dw.DimProduct")
        cursor.execute("DELETE FROM dw.DimCustomer")

# ----------------------------------------------------
# 1. LOAD CUSTOMER DIMENSION
# ----------------------------------------------------
        customer_rows = []

        seen_customer_ids = set()

        for row in customers:
            customer_id = str(row["customer_id"]).strip()

            if not customer_id or customer_id in seen_customer_ids:
                continue

            seen_customer_ids.add(customer_id)

            customer_name = str(row["customer_name"]).strip()
            email = str(row["email"]).strip() or None
            city = str(row["city"]).strip() or None

            try:
                signup_date = parse_date(row["signup_date"])
            except ValueError:
                signup_date = None

            customer_rows.append((
                customer_id,
                customer_name,
                email,
                city,
                signup_date,
            ))

        cursor.fast_executemany = True
        cursor.executemany(
            """
            INSERT INTO dw.DimCustomer
            (CustomerID, CustomerName, Email, City, SignupDate)
            VALUES (?, ?, ?, ?, ?)
            """,
            customer_rows,
        )

# ----------------------------------------------------
# 2. LOAD PRODUCT DIMENSION
# ----------------------------------------------------
        product_rows = []
        seen_product_ids = set()

        for row in products:
            product_id = str(row["product_id"]).strip()

            if not product_id or product_id in seen_product_ids:
                continue

            seen_product_ids.add(product_id)

            price = parse_decimal(row["unit_price"])

            if price < 0:
                raise ValueError(
                    f"Harga produk negatif: {product_id}"
                )

            product_rows.append((
                product_id,
                str(row["product_name"]).strip(),
                str(row["category"]).strip() or None,
                price,
            ))

        cursor.executemany(
            """
            INSERT INTO dw.DimProduct
            (ProductID, ProductName, Category, UnitPrice)
            VALUES (?, ?, ?, ?)
            """,
            product_rows,
        )

# ----------------------------------------------------
# 3. BUAT LOOKUP SURROGATE KEYS
# ----------------------------------------------------
        cursor.execute(
            "SELECT CustomerID, CustomerKey FROM dw.DimCustomer"
        )
        customer_keys = {
            row.CustomerID: row.CustomerKey
            for row in cursor.fetchall()
        }

        cursor.execute(
            "SELECT ProductID, ProductKey FROM dw.DimProduct"
        )
        product_keys = {
            row.ProductID: row.ProductKey
            for row in cursor.fetchall()
        }

# ----------------------------------------------------
# 4. LOAD DATE DIMENSION
# ----------------------------------------------------
        order_by_id = {}

# Simpan kemunculan pertama setiap order ID.
        for row in orders:
            order_id = str(row["order_id"]).strip()

            if order_id and order_id not in order_by_id:
                order_by_id[order_id] = row

        valid_dates = set()

        for row in order_by_id.values():
            try:
                order_date = parse_date(row["order_date"])
            except ValueError:
                continue

            if order_date:
                valid_dates.add(order_date)

        date_rows = []

        for d in sorted(valid_dates):
            date_rows.append((
                int(d.strftime("%Y%m%d")),
                d,
                d.year,
                (d.month - 1) // 3 + 1,
                d.month,
                d.strftime("%B"),
                d.day,
            ))

        if date_rows:
            cursor.executemany(
                """
                INSERT INTO dw.DimDate
                (DateKey, FullDate, [Year], [Quarter],
                [Month], MonthName, [Day])
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                date_rows,
            )

        date_keys = {
            d: int(d.strftime("%Y%m%d"))
            for d in valid_dates
        }

# ----------------------------------------------------
# 5. LOAD FACT SALES
# ----------------------------------------------------
        seen_item_ids = set()
        fact_rows = []

        skipped = {
            "duplicate_item": 0,
            "invalid_quantity": 0,
            "unknown_order": 0,
            "cancelled_order": 0,
            "unknown_customer": 0,
            "unknown_product": 0,
            "invalid_date": 0,
            "invalid_amount": 0,
        }

        for item in order_items:
            item_id = str(item["order_item_id"]).strip()

            if not item_id or item_id in seen_item_ids:
                skipped["duplicate_item"] += 1
                continue

            seen_item_ids.add(item_id)

            try:
                quantity = int(str(item["quantity"]).strip())
                unit_price = parse_decimal(item["unit_price"])
            except (ValueError, InvalidOperation):
                skipped["invalid_quantity"] += 1
                continue

            if quantity <= 0:
                skipped["invalid_quantity"] += 1
                continue

            if unit_price < 0:
                skipped["invalid_amount"] += 1
                continue

            order_id = str(item["order_id"]).strip()
            product_id = str(item["product_id"]).strip()

            order = order_by_id.get(order_id)

            if order is None:
                skipped["unknown_order"] += 1
                continue

            status = str(order["order_status"]).strip()

            if status.lower() == "cancelled":
                skipped["cancelled_order"] += 1
                continue

            customer_id = str(order["customer_id"]).strip()

            if customer_id not in customer_keys:
                skipped["unknown_customer"] += 1
                continue

            if product_id not in product_keys:
                skipped["unknown_product"] += 1
                continue

            try:
                order_date = parse_date(order["order_date"])
            except ValueError:
                order_date = None

            if order_date is None or order_date not in date_keys:
                skipped["invalid_date"] += 1
                continue

            sales_amount = quantity * unit_price

            fact_rows.append((
                item_id,
                order_id,
                customer_keys[customer_id],
                product_keys[product_id],
                date_keys[order_date],
                status,
                quantity,
                unit_price,
                sales_amount,
            ))

        if fact_rows:
            cursor.executemany(
                """
                INSERT INTO dw.FactSales
                (OrderItemID, OrderID, CustomerKey,
                ProductKey, DateKey, OrderStatus,
                Quantity, UnitPrice, SalesAmount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                fact_rows,
            )

        connection.commit()

        print("\n=== LOAD SUMMARY ===")
        print(f"DimCustomer: {len(customer_rows)}")
        print(f"DimProduct : {len(product_rows)}")
        print(f"DimDate : {len(date_rows)}")
        print(f"FactSales : {len(fact_rows)}")

        print("\n=== SKIPPED ROWS ===")
        for reason, count in skipped.items():
            print(f"{reason}: {count}")

        print("\nETL WAREHOUSE BERHASIL")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()