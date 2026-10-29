from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REJECTED_DIR = BASE_DIR / "data" / "rejected"
LOG_DIR = BASE_DIR / "logs"

STAGING_DATABASE = "ECommerceStaging"
WAREHOUSE_DATABASE = "ECommerceDW"

SQL_SERVER = "DESKTOP-D9BVEU4"
SQL_DRIVER = "ODBC Driver 18 for SQL Server"

REQUIRED_FILES = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
    "payments.csv",
    "shipments.csv",
]

STAGING_CONNECTION = (
    f"DRIVER={{{SQL_DRIVER}}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={STAGING_DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

WAREHOUSE_CONNECTION = (
    f"DRIVER={{{SQL_DRIVER}}};"
    f"SERVER={SQL_SERVER};"
    f"DATABASE={WAREHOUSE_DATABASE};"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)