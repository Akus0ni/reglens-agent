"""Token usage and cost per review (spec 0001, R1.16).

List prices per million tokens, as in RegLens ``ModelPricing.cs`` (checked against Anthropic's pricing for spec 0005).
"""

from collections.abc import Mapping
from typing import Any

PRICES_PER_MTOK: dict[str, tuple[float, float]] = {
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-haiku-4-5": (1.0, 5.0),
}

Usage = dict[str, dict[str, int]]


def usage_of(model: str, message: Any) -> Usage:
    """Input and output tokens from a LangChain ``AIMessage``'s ``usage_metadata``, keyed by model."""
    metadata = getattr(message, "usage_metadata", None) or {}
    return {model: {"input": int(metadata.get("input_tokens", 0)), "output": int(metadata.get("output_tokens", 0)),
                    "calls": 1}}


def merge_usage(left: Usage | None, right: Usage | None) -> Usage:
    """LangGraph reducer: adds token counts per model."""
    merged: Usage = {model: dict(counts) for model, counts in (left or {}).items()}
    for model, counts in (right or {}).items():
        total = merged.setdefault(model, {"input": 0, "output": 0, "calls": 0})
        for key, value in counts.items():
            total[key] = total.get(key, 0) + value
    return merged


def cost_usd(usage: Mapping[str, Mapping[str, int]]) -> float:
    """List-price cost of the recorded usage. An unknown model raises: a cost must never be silently zero."""
    total = 0.0
    for model, counts in usage.items():
        if model not in PRICES_PER_MTOK:
            raise KeyError(f"No price for model '{model}'.")
        input_price, output_price = PRICES_PER_MTOK[model]
        total += counts.get("input", 0) * input_price / 1e6 + counts.get("output", 0) * output_price / 1e6
    return total
