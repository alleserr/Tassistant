"""Module for fetching market data from Tinkoff Investments API."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import pandas as pd

# Placeholder for Tinkoff API client
try:
    from tinkoff.invest import Client, CandleInterval
except ImportError:  # pragma: no cover - library not available
    Client = Any  # type: ignore
    CandleInterval = Any  # type: ignore

logger = logging.getLogger(__name__)

class MarketDataFetcher:
    """Wrapper around Tinkoff Investments API for historical data."""

    def __init__(self, token: str, sandbox: bool = True) -> None:
        self.token = token
        self.sandbox = sandbox
        self._figi_cache: Dict[str, str] = {}

    def resolve_figi(self, ticker: str) -> Optional[str]:
        """Resolve ticker to FIGI, caching results."""
        ticker = ticker.upper()
        if ticker in self._figi_cache:
            return self._figi_cache[ticker]

        try:
            with Client(self.token) as client:  # type: ignore
                shares = client.instruments.shares().instruments
                for share in shares:
                    if share.ticker.upper() == ticker:
                        self._figi_cache[ticker] = share.figi
                        return share.figi
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Failed to resolve FIGI for %s: %s", ticker, exc)
        return None

    def get_candles(self, figi: str, days: int = 5):
        """Fetch historical candles for the given FIGI."""
        try:
            with Client(self.token) as client:  # type: ignore
                now = datetime.utcnow()
                start = now - timedelta(days=days)
                response = client.market_data.get_candles(
                    figi=figi,
                    from_=start,
                    to=now,
                    interval=CandleInterval.CANDLE_INTERVAL_15_MIN,
                )
                candles = [
                    {
                        "time": c.time,
                        "open": float(c.o),
                        "high": float(c.h),
                        "low": float(c.l),
                        "close": float(c.c),
                        "volume": c.v,
                    }
                    for c in response.candles
                ]
                logger.debug("Fetched %d candles for %s", len(candles), figi)
                return pd.DataFrame(candles)
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Failed to fetch data: %s", exc)
            return pd.DataFrame()

    def get_last_price(self, figi: str) -> Optional[float]:
        """Fetch the latest price for a given FIGI."""
        try:
            with Client(self.token) as client:  # type: ignore
                resp = client.market_data.get_last_prices(figi=[figi])
                if resp.last_prices:
                    price = resp.last_prices[0].price
                    return float(price.units) + price.nano / 1e9
        except Exception as exc:  # pragma: no cover - network errors
            logger.error("Failed to fetch last price: %s", exc)
        return None
