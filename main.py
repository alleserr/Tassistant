"""Entry point for the trading assistant bot."""

from __future__ import annotations

import logging

from .ai_core import PlannerAgent, TrendAgent, VolumeAgent
from .config import BotConfig
from .data_fetcher import MarketDataFetcher
from .strategies import calculate_indicators
from .telegram_bot import TelegramInterface
from .memory import Memory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run(config: BotConfig) -> None:
    fetcher = MarketDataFetcher(config.tinkoff_token, sandbox=config.sandbox)
    memory = Memory()
    trend_agent = TrendAgent(config.openai_token)
    volume_agent = VolumeAgent(config.openai_token)
    planner_agent = PlannerAgent(config.openai_token)

    async def create_plans(tickers: list[str]) -> str:
        results = []
        for ticker in tickers:
            figi = fetcher.resolve_figi(ticker)
            if not figi:
                results.append(f"{ticker}: тикер не найден")
                continue
            df = fetcher.get_candles(figi)
            if df.empty:
                results.append(f"{ticker}: нет данных")
                continue
            df = calculate_indicators(df)
            csv_data = df.tail(40).to_csv(index=False)
            trend = trend_agent.analyse(csv_data)
            volume = volume_agent.analyse(csv_data)
            plan_text = planner_agent.plan([trend, volume])
            memory.add_plan(ticker, plan_text)
            results.append(f"План для {ticker}\n{plan_text}")
        return "\n\n".join(results)

    async def status(tickers: list[str]) -> str:
        parts = []
        for ticker in tickers:
            figi = fetcher.resolve_figi(ticker)
            price = fetcher.get_last_price(figi) if figi else None
            rec = memory.latest_plan(ticker)
            info = f"{ticker}: "
            if price is not None:
                info += f"{price:.2f}"
            if rec:
                info += f" | {rec.status}"
            parts.append(info)
        return "\n".join(parts)

    async def track(ticker: str, state: bool) -> str:
        rec = memory.latest_plan(ticker)
        if not rec:
            return "Нет плана для слежения"
        memory.update_status(rec.id, "tracking" if state else "active")
        return ("Включено" if state else "Выключено") + f" слежение для {ticker}"

    bot = TelegramInterface(config.telegram_token)
    bot.start(create_plans, status, track)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit("Use this module as a library")
