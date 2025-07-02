"""LLM-based multi-agent core for generating trading plans."""

from __future__ import annotations

import logging
from typing import List

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None  # type: ignore

logger = logging.getLogger(__name__)


class BaseAgent:
    role: str

    def __init__(self, api_key: str):
        self.api_key = api_key
        if openai:
            openai.api_key = api_key

    def _ask(self, prompt: str) -> str:
        if not openai:  # pragma: no cover
            logger.warning("OpenAI library not installed. Returning fallback")
            return ""
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": self.role}, {"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content  # type: ignore


class TrendAgent(BaseAgent):
    role = (
        "You are AgentTrend. Analyse OHLCV data and indicators to identify trend and key levels."
    )

    def analyse(self, data: str) -> str:
        return self._ask(data)


class VolumeAgent(BaseAgent):
    role = (
        "You are AgentVolume. Interpret volume metrics and signal strength of buyers and sellers."
    )

    def analyse(self, data: str) -> str:
        return self._ask(data)


class PlannerAgent(BaseAgent):
    role = (
        "You are AgentPlanner. Using analysis from other agents, compose a concise trading plan in Russian."
    )

    def plan(self, analyses: List[str]) -> str:
        prompt = "\n".join(analyses)
        return self._ask(prompt)
