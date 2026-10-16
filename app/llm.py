
from __future__ import annotations

import json
import logging
import os
from datetime import date

from openai import AsyncOpenAI

# All AI requests go through OpenRouter.
# The OpenAI SDK is used only as an HTTP client.
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_client: AsyncOpenAI | None = None

_budget = {
    "day": date.today().isoformat(),
    "used": 0,
}
MIN_TOKENS = 4000

# Cumulative token usage, used by the evaluation runner.
USAGE = {
    "in": 0,
    "out": 0,
}

log = logging.getLogger("friday.llm")


def model() -> str:
    """Return the configured OpenRouter model ID."""
    return os.getenv(
        "FRIDAY_MODEL",
        "nvidia/nemotron-3.5-super-vl:free",
    )


def get_client() -> AsyncOpenAI:
    """Create and reuse the OpenRouter API client."""
    global _client

    if _client is None:
        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set in .env"
            )

        _client = AsyncOpenAI(
            api_key=api_key,
            base_url=_OPENROUTER_BASE_URL,
            timeout=60.0,
            max_retries=2,
        )

    return _client


def budget_ok() -> bool:
    """Check whether the daily token budget has remaining capacity."""
    today = date.today().isoformat()

    if _budget["day"] != today:
        _budget.update(day=today, used=0)

    limit = int(os.getenv("DAILY_TOKEN_BUDGET", "500000"))
    return _budget["used"] < limit


def add_usage(inp: int, out: int) -> None:
    """Record token usage for the current process."""
    USAGE["in"] += inp
    USAGE["out"] += out
    _budget["used"] += inp + out


async def complete(system: str, user: str, max_tokens: int = 800, model_name: str | None = None) -> str:
    if not budget_ok():
        raise RuntimeError("daily budget exhausted")

    resp = await get_client().chat.completions.create(
        model=model_name or model(),
       max_tokens=max(max_tokens, MIN_TOKENS),
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    if resp.usage is not None:
        add_usage(
            resp.usage.prompt_tokens,
            resp.usage.completion_tokens,
        )

    text = resp.choices[0].message.content or ""
    if not text.strip():
        log.warning(json.dumps({"event": "empty_completion", "stop": resp.choices[0].finish_reason,
                                "blocks": [], "out_tokens": resp.usage.completion_tokens if resp.usage else 0}))
    return text
