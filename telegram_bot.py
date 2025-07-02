"""Telegram bot interface."""

from __future__ import annotations

import logging
from typing import Awaitable, Callable, Dict, List

try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.utils import executor
except ImportError:  # pragma: no cover
    Bot = Dispatcher = types = executor = None  # type: ignore

logger = logging.getLogger(__name__)

class TelegramInterface:
    def __init__(self, token: str):
        if Bot is None:
            raise RuntimeError("aiogram not installed")
        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot)
        self.tickers: List[str] = []
        self.tracking: Dict[str, bool] = {}

    def start(
        self,
        on_plan: Callable[[List[str]], Awaitable[str]],
        on_status: Callable[[List[str]], Awaitable[str]],
        on_track: Callable[[str, bool], Awaitable[str]],
    ) -> None:

        @self.dp.message_handler(commands=["start"])
        async def cmd_start(message: types.Message):
            await message.reply("Привет! Используйте /watch <тикеры> чтобы добавить их.")

        @self.dp.message_handler(commands=["watch"])
        async def cmd_watch(message: types.Message):
            parts = message.text.split()[1:]
            self.tickers = [p.upper() for p in parts]
            await message.reply(f"Добавлены тикеры: {', '.join(self.tickers)}")

        @self.dp.message_handler(commands=["plan"])
        async def cmd_plan(message: types.Message):
            reply = await on_plan(self.tickers)
            await message.reply(reply)

        @self.dp.message_handler(commands=["status"])
        async def cmd_status(message: types.Message):
            reply = await on_status(self.tickers)
            await message.reply(reply)

        @self.dp.message_handler(commands=["track"])
        async def cmd_track(message: types.Message):
            parts = message.text.split()
            if len(parts) >= 3 and parts[1] in ("on", "off"):
                ticker = parts[2].upper()
                state = parts[1] == "on"
                self.tracking[ticker] = state
                reply = await on_track(ticker, state)
                await message.reply(reply)
            else:
                await message.reply("Использование: /track on|off TICKER")

        @self.dp.message_handler()
        async def fallback(message: types.Message):
            await message.reply("Неизвестная команда. Используйте /watch или /plan.")

        executor.start_polling(self.dp, skip_updates=True)
