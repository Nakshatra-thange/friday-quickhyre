
from __future__ import annotations

import os
from datetime import date

from openai import AsyncOpenAI

# All AI requests go through RapidRouter.
# The OpenAI SDK is used only as an HTTP client.
_RR_BASE_URL = "https://rapidrouter.ai/api/v1"

_client: AsyncOpenAI | None = None

_budget = {
    "day": date.today().isoformat(),
    "used": 0,
}

# Cumulative token usage, used by the evaluation runner.
USAGE = {
    "in": 0,
    "out": 0,
}


def model() -> str:
    """Return the configured RapidRouter model ID."""
    return os.getenv(
        "FRIDAY_MODEL",
        "nvidia/nvidia-nemotron-3-super-120b-a12b:free",
    )


def get_client() -> AsyncOpenAI:
    """Create and reuse the RapidRouter API client."""
    global _client

    if _client is None:
        api_key = os.getenv("RAPIDROUTER_API_KEY")

        if not api_key:
            raise RuntimeError(
                "RAPIDROUTER_API_KEY is not set in .env"
            )

        _client = AsyncOpenAI(
            api_key=api_key,
            base_url=_RR_BASE_URL,
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


async def complete(
    system: str,
    user: str,
    max_tokens: int = 800,
    model_name: str | None = None,
) -> str:
    """Send a chat completion request through RapidRouter."""
    if not budget_ok():
        raise RuntimeError("Daily token budget exhausted")

    response = await get_client().chat.completions.create(
        model=model_name or model(),
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    if response.usage is not None:
        add_usage(
            response.usage.prompt_tokens,
            response.usage.completion_tokens,
        )

    return response.choices[0].message.content or ""
