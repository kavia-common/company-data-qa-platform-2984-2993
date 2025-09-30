"""
Embedding provider abstraction.

This module exposes a function to compute embeddings for texts. If OPENAI_API_KEY
is not set, it falls back to a deterministic hash-based vector for demo usage.
"""
from __future__ import annotations
import hashlib
from typing import List

import numpy as np  # type: ignore

from .config import SETTINGS

try:
    from openai import OpenAI  # type: ignore
except Exception:  # pragma: no cover
    OpenAI = None


def _fallback_vector(text: str, dim: int) -> List[float]:
    """
    Create a deterministic pseudo-embedding from text to allow the system to operate
    without external dependencies. Not semantically meaningful but stable.
    """
    h = hashlib.sha256(text.encode("utf-8")).digest()
    # repeat hash to reach dim
    arr = []
    while len(arr) < dim:
        for b in h:
            arr.append((b / 255.0) * 2 - 1)  # map to [-1, 1]
            if len(arr) >= dim:
                break
    # normalize
    vec = np.array(arr, dtype="float32")
    n = np.linalg.norm(vec)
    if n == 0:
        return vec.tolist()
    return (vec / n).tolist()


# PUBLIC_INTERFACE
def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Compute embeddings for a list of texts.

    Returns:
        List[List[float]]: embedding vectors (dim = SETTINGS.embedding_dim)
    """
    api_key = SETTINGS.openai_api_key
    model = SETTINGS.embedding_model
    dim = SETTINGS.embedding_dim

    if not api_key or OpenAI is None:
        return [_fallback_vector(t, dim) for t in texts]

    client = OpenAI(api_key=api_key)
    # OpenAI new client returns .data as list of {embedding: [...]}
    resp = client.embeddings.create(input=texts, model=model)
    vectors: List[List[float]] = [d.embedding for d in resp.data]
    return vectors
