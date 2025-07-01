from dataclasses import dataclass

@dataclass
class BotConfig:
    """Configuration for the trading assistant."""

    tinkoff_token: str
    telegram_token: str
    openai_token: str
    tickers: list[str]
    sandbox: bool = True
