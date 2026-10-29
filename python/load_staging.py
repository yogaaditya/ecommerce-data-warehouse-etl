
from pathlib import Path

import pandas as pd
import pyodbc


# ============================================================
# KONFIGURASI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

SERVER = "localhost"
DATABASE = "ECommerceStaging"
DRIVER = "ODBC Driver 18 for SQL Server"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# CSV -> nama tabel staging
TABLES = {
    "customers.csv": "Customers",
    "products.csv": "Products",
    "orders.csv": "Orders",
    "order_items.csv": "OrderItems",
    "payments.csv": "Payments",
    "shipments.csv": "Shipments",
}


def load_table(connection, filename, table_name):
    csv_path = RAW_DIR / filename

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV tidak ditemukan: {csv_path}")

# Baca seluruh kolom sebagai teks agar nilai sumber
# tidak otomatis diubah atau dibuang oleh pandas.
    df = pd.read_csv(
        csv_path,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    columns = list(df.columns)

# Nama tabel dan kolom berasal dari konfigurasi tetap,
# bukan dari input bebas pengguna.
    column_sql = ", ".join(f"[{col}]" for col in columns)
    placeholders = ", ".join("?" for _ in columns)

    sql = (
        f"INSERT INTO stg.[{table_name}] "
        f"({column_sql}) VALUES ({placeholders})"
    )

    rows = [
        tuple(value for value in row)
        for row in df.itertuples(index=False, name=None)
    ]

    if rows:
        cursor = connection.cursor()
        cursor.fast_executemany = True
        cursor.executemany(sql, rows)
        cursor.close()

    print(f"{filename} -> stg.{table_name}: {len(rows)} baris")
    return len(rows)


def main():
    print("Memulai proses load staging...")

    with pyodbc.connect(CONNECTION_STRING) as connection:
        cursor = connection.cursor()

# Mencegah data bertambah ganda ketika skrip diulang.
# Gunakan hanya pada database staging khusus project ini.
        for table_name in TABLES.values():
            cursor.execute(f"DELETE FROM stg.[{table_name}]")

        cursor.close()
        connection.commit()

        total_rows = 0

        try:
            for filename, table_name in TABLES.items():
                total_rows += load_table(
                    connection,
                    filename,
                    table_name,
                )

            connection.commit()
            print(f"\nLOAD BERHASIL: {total_rows} baris dimuat.")

        except Exception:
            connection.rollback()
            raise


if __name__ == "__main__":
    main()