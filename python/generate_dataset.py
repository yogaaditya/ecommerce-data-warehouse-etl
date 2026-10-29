import csv
import random
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

random.seed(42)


def write_csv(filename, rows):
    path = RAW_DIR / filename

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"{filename}: {len(rows)} baris")


customer_data = [
    ("Andi Pratama", "andi@example.com", "Jakarta", "2025-01-10"),
    ("Budi Santoso", "budi@example.com", "Bandung", "2025-01-15"),
    ("Citra Lestari", "citra@example.com", "Surabaya", "2025-02-02"),
    ("Dewi Anggraini", "dewi@example.com", "Yogyakarta", "2025-02-20"),
    ("Eko Saputra", "eko@example.com", "Semarang", "2025-03-05"),
    ("Fitri Amelia", "fitri@example.com", "Jakarta", "2025-03-12"),
    ("Gilang Ramadhan", "gilang@example.com", "Malang", "2025-04-01"),
    ("Hana Putri", "hana@example.com", "Bandung", "2025-04-18"),
    ("Indra Wijaya", "", "Surabaya", "2025-05-09"),
    ("Joko Firmansyah", "joko@example.com", "Medan", "2025-05-20"),
    ("Kartika Sari", "kartika@example.com", "Denpasar", "2025-06-02"),
    ("Lukman Hakim", "lukman@example.com", "Makassar", "2025-06-15"),
]

customers = [
    {
        "customer_id": f"C{i:03}",
        "customer_name": name,
        "email": email,
        "city": city,
        "signup_date": signup,
    }
    for i, (name, email, city, signup) in enumerate(customer_data, start=1)
]

products = [
    {"product_id": "P001", "product_name": "Wireless Mouse", "category": "Accessories", "unit_price": 125000},
    {"product_id": "P002", "product_name": "Mechanical Keyboard", "category": "Accessories", "unit_price": 450000},
    {"product_id": "P003", "product_name": "USB-C Hub", "category": "Accessories", "unit_price": 275000},
    {"product_id": "P004", "product_name": "Webcam HD", "category": "Electronics", "unit_price": 390000},
    {"product_id": "P005", "product_name": "Headset", "category": "Audio", "unit_price": 220000},
    {"product_id": "P006", "product_name": "Laptop Stand", "category": "Accessories", "unit_price": 180000},
    {"product_id": "P007", "product_name": "SSD 1TB", "category": "Storage", "unit_price": 950000},
    {"product_id": "P008", "product_name": "Monitor 24 inch", "category": "Electronics", "unit_price": 1750000},
]

orders = []

for i in range(1, 26):
    orders.append({
        "order_id": f"O{i:04}",
        "customer_id": random.choice(customers)["customer_id"],
        "order_date": f"2026-{random.randint(1, 9):02}-{random.randint(1, 28):02}",
        "order_status": random.choice(
            ["Completed", "Completed", "Processing", "Cancelled"]
        ),
    })

# Sengaja menambahkan satu baris order duplikat.
orders.append(orders[4].copy())

order_items = []
line_number = 1

for order in orders[:25]:
    for _ in range(random.randint(1, 3)):
        product = random.choice(products)

        order_items.append({
            "order_item_id": f"OI{line_number:04}",
            "order_id": order["order_id"],
            "product_id": product["product_id"],
            "quantity": random.randint(1, 3),
            "unit_price": product["unit_price"],
        })

        line_number += 1

# Anomali yang sengaja dibuat untuk latihan data quality.
order_items[0]["quantity"] = 0
order_items[1]["quantity"] = -2
order_items[2]["product_id"] = "P999"
order_items.append(order_items[3].copy())

payments = []

for i, order in enumerate(orders[:25], start=1):
    payments.append({
        "payment_id": f"PAY{i:04}",
        "order_id": order["order_id"],
        "payment_method": random.choice(
            ["Bank Transfer", "E-Wallet", "Credit Card", "COD"]
        ),
        "payment_status": random.choice(["Paid", "Paid", "Pending", "Failed"]),
        "payment_date": order["order_date"],
    })

shipments = []

for i, order in enumerate(orders[:25], start=1):
    status = random.choice(["Delivered", "Shipped", "Processing"])

    shipments.append({
        "shipment_id": f"SHP{i:04}",
        "order_id": order["order_id"],
        "shipment_status": status,
        "shipped_date": (
            order["order_date"] if status in ("Shipped", "Delivered") else ""
        ),
        "delivered_date": (
            order["order_date"] if status == "Delivered" else ""
        ),
    })

write_csv("customers.csv", customers)
write_csv("products.csv", products)
write_csv("orders.csv", orders)
write_csv("order_items.csv", order_items)
write_csv("payments.csv", payments)
write_csv("shipments.csv", shipments)

print("\nDataset E-Commerce berhasil dibuat.")