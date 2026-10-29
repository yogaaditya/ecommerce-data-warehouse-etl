
import sys
from decimal import Decimal
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from python.etl_utils import (
    calculate_sales_amount,
    validate_quantity,
    validate_unit_price,
)


@pytest.mark.parametrize(
    "value",
    [1, 2, 3, "1", "2", "3", "1.0"],
)
def test_valid_quantity(value):
    assert validate_quantity(value) is True


@pytest.mark.parametrize(
    "value",
    [0, -1, "-2", "abc", "", "1.5", None, "NaN", "Infinity"],
)
def test_invalid_quantity(value):
    assert validate_quantity(value) is False


@pytest.mark.parametrize(
    "value",
    ["125000", 125000, "0", "99.50"],
)
def test_valid_unit_price(value):
    assert validate_unit_price(value) is True


@pytest.mark.parametrize(
    "value",
    ["-1", "abc", "", None, "NaN", "Infinity"],
)
def test_invalid_unit_price(value):
    assert validate_unit_price(value) is False


def test_calculate_sales_amount():
    result = calculate_sales_amount(2, "125000")
    assert result == Decimal("250000.00")


def test_calculate_sales_amount_rejects_invalid_quantity():
    with pytest.raises(ValueError):
        calculate_sales_amount(0, 125000)


def test_calculate_sales_amount_rejects_negative_price():
    with pytest.raises(ValueError):
        calculate_sales_amount(2, -100)