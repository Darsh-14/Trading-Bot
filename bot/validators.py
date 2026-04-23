from decimal import Decimal
from decimal import InvalidOperation
from dataclasses import asdict
from dataclasses import dataclass
from typing import Optional

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}


@dataclass(frozen=True)
class OrderInput:
    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Optional[Decimal] = None


def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str],
) -> OrderInput:
    normalized_symbol = validate_symbol(symbol)
    normalized_side = validate_side(side)
    normalized_order_type = validate_order_type(order_type)
    normalized_quantity = validate_decimal_field(quantity, "quantity")
    normalized_price = validate_decimal_field(price, "price") if price is not None else None

    if normalized_order_type == "LIMIT" and normalized_price is None:
        raise ValueError("Price is required for LIMIT orders.")

    if normalized_order_type == "MARKET" and normalized_price is not None:
        raise ValueError("Price should not be supplied for MARKET orders.")

    return OrderInput(
        symbol=normalized_symbol,
        side=normalized_side,
        order_type=normalized_order_type,
        quantity=normalized_quantity,
        price=normalized_price,
    )


def validate_symbol(symbol: str) -> str:
    normalized = symbol.strip().upper()
    if not normalized:
        raise ValueError("Symbol cannot be empty.")
    if not normalized.endswith("USDT"):
        raise ValueError("Only USDT-M futures symbols are supported. Example: BTCUSDT")
    return normalized


def validate_side(side: str) -> str:
    normalized = side.strip().upper()
    if normalized not in VALID_SIDES:
        raise ValueError("Side must be BUY or SELL.")
    return normalized


def validate_order_type(order_type: str) -> str:
    normalized = order_type.strip().upper()
    if normalized not in VALID_ORDER_TYPES:
        raise ValueError("Order type must be MARKET or LIMIT.")
    return normalized


def validate_decimal_field(value: str, field_name: str) -> Decimal:
    try:
        decimal_value = Decimal(value.strip())
    except (AttributeError, InvalidOperation) as exc:
        raise ValueError(f"Invalid {field_name}: {value}") from exc

    if decimal_value <= 0:
        raise ValueError(f"{field_name.capitalize()} must be greater than zero.")

    return decimal_value
