import logging
import time
from dataclasses import asdict
from typing import Any
from typing import Optional

from .client import BinanceFuturesClient
from .validators import OrderInput
from .validators import validate_order_input


class OrderManager:
    def __init__(self, client: Optional[BinanceFuturesClient] = None) -> None:
        self.client = client or BinanceFuturesClient()
        self.logger = logging.getLogger(__name__)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: str,
        price: Optional[str] = None,
) -> dict[str, Any]:
        order_request = validate_order_input(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
        )

        self.logger.info("validated_order=%s", asdict(order_request))

        response = self.client.place_order(
            symbol=order_request.symbol,
            side=order_request.side,
            order_type=order_request.order_type,
            quantity=order_request.quantity,
            price=order_request.price,
        )

        response = self._sync_market_order(order_request, response)

        return {
            "request": asdict(order_request),
            "response": response,
        }

    def _sync_market_order(self, order_request: OrderInput, response: dict[str, Any]) -> dict[str, Any]:
        if not response.get("orderId") or order_request.order_type != "MARKET":
            return response
        return self._refresh_market_order(symbol=order_request.symbol, order_id=int(response["orderId"]), initial_response=response)

    def _refresh_market_order(self, symbol: str, order_id: int, initial_response: dict[str, Any]) -> dict[str, Any]:
        latest_response = initial_response

        for _ in range(3):
            status = latest_response.get("status")
            executed_qty = latest_response.get("executedQty")
            if status == "FILLED" or executed_qty not in {None, "0", "0.0", "0.0000"}:
                return latest_response

            time.sleep(1)
            latest_response = self.client.get_order(symbol=symbol, order_id=order_id)
            self.logger.info("market_order_refresh=%s", latest_response)

        return latest_response
