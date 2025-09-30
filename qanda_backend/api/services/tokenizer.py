"""
Simple token counting utility. For demo purposes we use tiktoken if available,
otherwise we fall back to a rough word-based counter.
"""
from __future__ import annotations
from typing import Optional

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None


def count_tokens(text: str, model: Optional[str] = None) -> int:
    """
    PUBLIC_INTERFACE
    Count tokens in a text string using tiktoken if available, else fallback.

    Args:
        text: the input text
        model: optional LLM model id to pick the right encoding

    Returns:
        int: approximate number of tokens
    """
    if not text:
        return 0
    if tiktoken:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    # naive fallback
    return max(1, len(text.split()))
