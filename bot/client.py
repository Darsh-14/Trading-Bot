import hashlib
import hmac
import logging
import os
import time
from decimal import Decimal
from typing import Optional
from urllib.parse import urlencode

import requests
from dotenv import load_dotenv

load_dotenv()


class BinanceClientError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 15,
    ) -> None:
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        self.base_url = (base_url or os.getenv("BINANCE_BASE_URL") or "https://testnet.binancefuture.com").rstrip("/")
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.time_offset = 0

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "Missing Binance API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET in your environment or .env file."
            )

        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Decimal,
        price: Optional[Decimal] = None,
    ) -> dict[str, object]:
        payload = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": self._format_decimal(quantity),
            "recvWindow": 10000,
            "timestamp": self._timestamp(),
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            payload["price"] = self._format_decimal(price)
            payload["timeInForce"] = "GTC"

        return self._signed_request("POST", "/fapi/v1/order", payload)

    def get_order(self, symbol: str, order_id: int) -> dict[str, object]:
        payload = {
            "symbol": symbol,
            "orderId": order_id,
            "recvWindow": 10000,
            "timestamp": self._timestamp(),
        }
        return self._signed_request("GET", "/fapi/v1/order", payload)

    def _signed_request(self, method: str, path: str, params: dict[str, object]) -> dict[str, object]:
        query_string = urlencode(params)
        signature = hmac.new(self.api_secret.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
        signed_params = {**params, "signature": signature}
        url = f"{self.base_url}{path}"

        self.logger.info(
            "binance_request method=%s url=%s params=%s",
            method,
            url,
            self._mask_sensitive(signed_params),
        )

        try:
            response = self.session.request(method=method, url=url, params=signed_params, timeout=self.timeout)
            response.raise_for_status()
        except requests.HTTPError as exc:
            error_text = exc.response.text if exc.response is not None else str(exc)
            self.logger.error("binance_http_error status=%s body=%s", getattr(exc.response, "status_code", "unknown"), error_text)
            if '"code":-1021' in error_text:
                self._sync_time()
            raise BinanceClientError(f"Binance API error: {error_text}") from exc
        except requests.RequestException as exc:
            self.logger.error("binance_network_error error=%s", exc)
            raise BinanceClientError(f"Network error while calling Binance: {exc}") from exc

        data = response.json()
        self.logger.info("binance_response status=%s body=%s", response.status_code, data)
        return data

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        return format(value.normalize(), "f")

    def _timestamp(self) -> int:
        if not self.time_offset:
            self._sync_time()
        return int(time.time() * 1000) + self.time_offset

    def _sync_time(self) -> None:
        url = f"{self.base_url}/fapi/v1/time"
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        server_time = response.json()["serverTime"]
        self.time_offset = int(server_time) - int(time.time() * 1000)
        self.logger.info("time_sync offset_ms=%s", self.time_offset)

    @staticmethod
    def _mask_sensitive(params: dict[str, object]) -> dict[str, object]:
        masked = dict(params)
        if "signature" in masked:
            masked["signature"] = "***masked***"
        return masked
