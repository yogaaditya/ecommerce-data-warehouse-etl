from decimal import Decimal, InvalidOperation


def validate_quantity(value):
    """Quantity valid jika merupakan bilangan bulat positif."""
    try:
        quantity = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        return False

    return (
        quantity.is_finite()
        and quantity > 0
        and quantity == quantity.to_integral_value()
    )


def validate_unit_price(value):
    """Harga valid jika numerik, finite, dan tidak negatif."""
    try:
        price = Decimal(str(value).strip())
    except (InvalidOperation, ValueError, TypeError):
        return False

    return price.is_finite() and price >= 0


def calculate_sales_amount(quantity, unit_price):
    """Menghitung nilai penjualan dari quantity dan harga."""
    if not validate_quantity(quantity):
        raise ValueError("Quantity harus berupa bilangan bulat positif.")

    if not validate_unit_price(unit_price):
        raise ValueError("Unit price harus numerik dan tidak negatif.")

    amount = Decimal(str(quantity)) * Decimal(str(unit_price))
    return amount.quantize(Decimal("0.01"))