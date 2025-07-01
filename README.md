# Trading Assistant

This project implements an experimental trading assistant bot following the
requirements from `Task.md`. The bot communicates with Telegram, fetches market
data from the Tinkoff Investments API, calculates technical indicators with
`pandas-ta`, and uses a small multi-agent LLM core to produce trading plans.
Plans are stored in a local SQLite database so the bot can remember previous
recommendations.

## Features

- Modular architecture (`data_fetcher`, `strategies`, `ai_core`, `telegram_bot`).
- Uses sandbox access to the broker API by default.
- Integration with OpenAI for generating trading plans.
- Easily extensible for new strategies or agents.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Create a configuration and run the bot:
   ```python
   from tassistant.config import BotConfig
   from tassistant.main import run

   config = BotConfig(
       tinkoff_token="<TINKOFF_TOKEN>",
       telegram_token="<TELEGRAM_TOKEN>",
       openai_token="<OPENAI_TOKEN>",
       tickers=["AAPL"],
   )
   run(config)
   ```

When the bot is running you can manage it through the following commands in
Telegram:

- `/watch TICKER1 TICKER2` – set the list of tickers to analyse.
- `/plan` – generate trading plans for all watched tickers.
- `/status` – show the last known price and plan status.
- `/track on|off TICKER` – toggle monitoring for a ticker.

Note: API keys are required for Telegram, Tinkoff, and OpenAI.
