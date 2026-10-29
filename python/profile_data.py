
from pathlib import Path

import pandas as pd


# ============================================================
# KONFIGURASI
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
REJECTED_DIR = BASE_DIR / "data" / "rejected"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REJECTED_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "customers.csv": "customer_id",
    "products.csv": "product_id",
    "orders.csv": "order_id",
    "order_items.csv": "order_item_id",
    "payments.csv": "payment_id",
    "shipments.csv": "shipment_id",
}


# ============================================================
# FUNGSI BANTU
# ============================================================

def load_csv(filename):
    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"File tidak ditemukan: {path}")

    return pd.read_csv(path, encoding="utf-8-sig")


def add_issue(
    issues,
    filename,
    record_key,
    field,
    value,
    severity,
    rule,
    description,
):
    issues.append({
        "source_file": filename,
        "record_key": str(record_key),
        "field": field,
        "value": str(value),
        "severity": severity,
        "rule": rule,
        "description": description,
    })


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 60)
print("ECOMMERCE DATA PROFILING")
print("=" * 60)

dataframes = {}

for filename in FILES:
    df = load_csv(filename).fillna("")
    dataframes[filename] = df
    print(f"Loaded {filename}: {len(df)} baris")

customers = dataframes["customers.csv"]
products = dataframes["products.csv"]
orders = dataframes["orders.csv"]
order_items = dataframes["order_items.csv"]
payments = dataframes["payments.csv"]
shipments = dataframes["shipments.csv"]

issues = []


# ============================================================
# 1. CEK DUPLIKASI PRIMARY KEY
# ============================================================

for filename, primary_key in FILES.items():
    df = dataframes[filename]

    duplicate_mask = df.duplicated(
        subset=[primary_key],
        keep="first",
    )

for _, row in df.loc[duplicate_mask].iterrows():
    add_issue(
        issues=issues,
        filename=filename,
        record_key=row[primary_key],
        field=primary_key,
        value=row[primary_key],
        severity="ERROR",
        rule="DUPLICATE_PRIMARY_KEY",
        description=f"Duplikasi nilai {primary_key}",
    )


# ============================================================
# 2. CEK EMAIL KOSONG
# ============================================================

for _, row in customers.iterrows():
    if not str(row["email"]).strip():
        add_issue(
            issues,
            "customers.csv",
            row["customer_id"],
            "email",
            "",
            "WARNING",
            "MISSING_EMAIL",
            "Email customer kosong",
        )


# ============================================================
# 3. CEK QUANTITY TIDAK VALID
# ============================================================

for _, row in order_items.iterrows():
    try:
        quantity = float(row["quantity"])
    except (ValueError, TypeError):
        quantity = None

if quantity is None or quantity <= 0:
    add_issue(
        issues,
        "order_items.csv",
        row["order_item_id"],
        "quantity",
        row["quantity"],
        "ERROR",
        "INVALID_QUANTITY",
        "Quantity harus berupa angka lebih besar dari nol",
    )


# ============================================================
# 4. CEK PRODUCT ID YANG TIDAK ADA DI MASTER PRODUK
# ============================================================

valid_product_ids = set(products["product_id"].astype(str))

for _, row in order_items.iterrows():
    product_id = str(row["product_id"])

    if product_id not in valid_product_ids:
        add_issue(
            issues,
            "order_items.csv",
            row["order_item_id"],
            "product_id",
            product_id,
            "ERROR",
            "UNKNOWN_PRODUCT_ID",
            "Product ID tidak ditemukan di products",
        )


# ============================================================
# 5. CEK REFERENSI ORDER
# ============================================================

valid_order_ids = set(orders["order_id"].astype(str))

for filename in ["order_items.csv", "payments.csv", "shipments.csv"]:
    df = dataframes[filename]

    for _, row in df.iterrows():
        order_id = str(row["order_id"])

        if order_id not in valid_order_ids:
            add_issue(
                issues,
                filename,
                row.iloc[0],
                "order_id",
                order_id,
                "ERROR",
                "UNKNOWN_ORDER_ID",
                "Order ID tidak ditemukan di orders",
            )


# ============================================================
# 6. SIMPAN LAPORAN MASALAH
# ============================================================

issue_columns = [
    "source_file",
    "record_key",
    "field",
    "value",
    "severity",
    "rule",
    "description",
]

issues_df = pd.DataFrame(issues, columns=issue_columns)

issues_path = PROCESSED_DIR / "data_quality_issues.csv"
issues_df.to_csv(issues_path, index=False, encoding="utf-8-sig")


# ============================================================
# 7. SIMPAN ORDER ITEMS YANG BERMASALAH
# ============================================================

invalid_item_keys = set(
    issues_df.loc[
        issues_df["source_file"] == "order_items.csv",
        "record_key",
    ].astype(str)
)

invalid_items = order_items[
    order_items["order_item_id"].astype(str).isin(invalid_item_keys)
].copy()

invalid_items["issue_types"] = invalid_items["order_item_id"].astype(
    str
).map(
    issues_df.loc[
        issues_df["source_file"] == "order_items.csv"
    ].groupby("record_key")["rule"].agg(
        lambda rules: ";".join(sorted(set(rules)))
    )
)

invalid_items_path = REJECTED_DIR / "invalid_order_items.csv"
invalid_items.to_csv(
    invalid_items_path,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 8. BUAT RINGKASAN PROFILING
# ============================================================

summary_rows = []

for filename, primary_key in FILES.items():
    df = dataframes[filename]

    blank_cells = int(
        df.astype(str)
        .apply(lambda column: column.str.strip().eq("").sum())
        .sum()
    )

duplicate_keys = int(
    df.duplicated(subset=[primary_key], keep="first").sum()
)

file_issues = int(
    (issues_df["source_file"] == filename).sum()
)

summary_rows.append({
    "source_file": filename,
    "row_count": len(df),
    "column_count": len(df.columns),
    "blank_cells": blank_cells,
    "duplicate_primary_keys": duplicate_keys,
    "issue_count": file_issues,
    "status": "ISSUES_FOUND" if file_issues else "PASSED",
})

summary_df = pd.DataFrame(summary_rows)

summary_path = PROCESSED_DIR / "data_quality_summary.csv"
summary_df.to_csv(
    summary_path,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 9. TAMPILKAN HASIL
# ============================================================

print("\n=== RINGKASAN DATA QUALITY ===")
print(summary_df.to_string(index=False))

print("\n=== JUMLAH MASALAH BERDASARKAN RULE ===")

if issues_df.empty:
        print("Tidak ditemukan masalah.")
else:
    print(
        issues_df.groupby(["source_file", "rule"])
        .size()
        .rename("jumlah")
        .to_string()
    )

print("\n=== FILE LAPORAN ===")
print(f"Summary : {summary_path}")
print(f"Issues : {issues_path}")
print(f"Rejected: {invalid_items_path}")

print("\nDATA PROFILING SELESAI")