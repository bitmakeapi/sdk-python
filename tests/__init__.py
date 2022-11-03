import decimal


def is_number(val: str) -> bool:
    try:
        decimal.Decimal(val)
        return True
    except decimal.InvalidOperation:
        return False
