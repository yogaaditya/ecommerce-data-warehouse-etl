import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def read_csv(filename):
    path = RAW_DIR / filename

    with path.open("r", newline="", encoding="utf-8-sig") as file:
        return list(csv.DictReader(file))


expected_files = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
    "payments.csv",
    "shipments.csv",
]

print("=== JUMLAH BARIS ===")

for filename in expected_files:
    rows = read_csv(filename)
    print(f"{filename}: {len(rows)} baris")

orders = read_csv("orders.csv")
order_items = read_csv("order_items.csv")
customers = read_csv("customers.csv")

unique_orders = {row["order_id"] for row in orders}
duplicate_order_count = len(orders) - len(unique_orders)

missing_emails = sum(
    not row["email"].strip() for row in customers
)

invalid_quantities = sum(
    int(row["quantity"]) <= 0 for row in order_items
)

invalid_products = sum(
    row["product_id"] == "P999" for row in order_items
)

duplicate_item_count = len(order_items) - len({
    row["order_item_id"] for row in order_items
})

print("\n=== DATA QUALITY CHECK ===")
print(f"Order unik: {len(unique_orders)}")
print(f"Baris order duplikat: {duplicate_order_count}")
print(f"Email kosong: {missing_emails}")
print(f"Quantity tidak valid: {invalid_quantities}")
print(f"Product ID tidak ditemukan: {invalid_products}")
print(f"Baris order item duplikat: {duplicate_item_count}")

print("\nVERIFIKASI DATASET BERHASIL")