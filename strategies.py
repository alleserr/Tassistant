"""Trading strategies and indicator calculations."""

from __future__ import annotations

import pandas as pd
import pandas_ta as ta


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add common technical indicators to the dataframe."""
    df = df.copy()
    df["ema_fast"] = ta.ema(df["close"], length=12)
    df["ema_slow"] = ta.ema(df["close"], length=26)
    df["rsi"] = ta.rsi(df["close"], length=14)
    df["vol_ma"] = ta.sma(df["volume"], length=20)
    return df
