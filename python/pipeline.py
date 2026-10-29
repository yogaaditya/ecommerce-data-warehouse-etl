import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pyodbc

from python.config import (
    BASE_DIR,
    LOG_DIR,
    RAW_DIR,
    REQUIRED_FILES,
    STAGING_CONNECTION,
    WAREHOUSE_CONNECTION,
)


# ============================================================
# LOGGING
# ============================================================

LOG_DIR.mkdir(parents=True, exist_ok=True)

log_file = LOG_DIR / "etl_pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
    logging.FileHandler(log_file, encoding="utf-8"),
    logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger("ecommerce_etl")


# ============================================================
# PRE-FLIGHT VALIDATION
# ============================================================

def validate_source_files():
    missing_files = [
        filename
        for filename in REQUIRED_FILES
        if not (RAW_DIR / filename).is_file()
    ]

    if missing_files:
        raise FileNotFoundError(
            "CSV sumber tidak ditemukan: " + ", ".join(missing_files)
        )

    logger.info(
        "Validasi file sumber berhasil: %s file",
        len(REQUIRED_FILES),
    )


def validate_database_connections():
    for database_name, connection_string in [
        ("ECommerceStaging", STAGING_CONNECTION),
        ("ECommerceDW", WAREHOUSE_CONNECTION),
    ]:
        with pyodbc.connect(connection_string, timeout=10) as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT DB_NAME()")
            actual_database = cursor.fetchone()[0]
            cursor.close()

        if actual_database != database_name:
            raise RuntimeError(
                f"Database yang terhubung tidak sesuai: {actual_database}"
            )

        logger.info("Koneksi database berhasil: %s", database_name)


# ============================================================
# RUN ETL SCRIPTS
# ============================================================

def run_script(script_name):
    script_path = BASE_DIR / "python" / script_name

    if not script_path.is_file():
        raise FileNotFoundError(f"Script tidak ditemukan: {script_path}")

    logger.info("Memulai script: %s", script_name)

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=BASE_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if result.stdout:
        for line in result.stdout.splitlines():
            logger.info("[%s] %s", script_name, line)

    if result.stderr:
        for line in result.stderr.splitlines():
            logger.error("[%s] %s", script_name, line)

    if result.returncode != 0:
        raise RuntimeError(
            f"Script {script_name} gagal dengan "
            f"exit code {result.returncode}"
        )

    logger.info("Script berhasil: %s", script_name)


# ============================================================
# MAIN PIPELINE
# ============================================================

def main():
    started_at = datetime.now()

    logger.info("=" * 60)
    logger.info("ECOMMERCE ETL PIPELINE DIMULAI")

    try:
        validate_source_files()
        validate_database_connections()

        run_script("load_staging.py")
        run_script("profile_data.py")
        run_script("load_warehouse.py")

        duration = (datetime.now() - started_at).total_seconds()

        logger.info(
            "PIPELINE BERHASIL. Durasi: %.2f detik",
            duration,
        )

    except Exception:
        logger.exception("PIPELINE GAGAL")
        raise


if __name__ == "__main__":
    main()