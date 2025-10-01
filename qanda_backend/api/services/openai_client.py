"""
OpenAI chat client wrapper. Falls back to a local template if API key is missing.
"""
from __future__ import annotations
from typing import List, Dict

from .config import SETTINGS

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None


SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions strictly using the provided context. "
    "If the answer cannot be derived from the context, say you don't know."
)


def _fallback_answer(question: str, context_snippets: List[str]) -> str:
    if not context_snippets:
        return "I'm not sure based on the available documents."
    return f"Based on the documents fallback: {context_snippets[0][:200]} ... Therefore: This is a suggested answer to '{question}'. "


# PUBLIC_INTERFACE
def generate_answer(question: str, context_snippets: List[str]) -> Dict:
    """
    Generate an answer using OpenAI if possible, otherwise return a fallback message.

    Returns:
        dict: {text, model, meta}
    """
    api_key = SETTINGS.openai_api_key
    model = SETTINGS.openai_model
    if not api_key or OpenAI is None:
        text = _fallback_answer(question, context_snippets)
        return {"text": text, "model": "fallback-local", "meta": {"reason": "no_api_key"}}

    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Question: {question}\n\nContext:\n" + "\n\n---\n\n".join(context_snippets),
        },
    ]
    resp = client.chat.completions.create(model=model, messages=messages, temperature=SETTINGS.generation_temperature)
    choice = resp.choices[0]
    text = choice.message.content or ""
    return {"text": text, "model": model, "meta": {"usage": getattr(resp, "usage", {})}}
