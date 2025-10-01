"""
Configuration utilities.

No environment variables are assumed to be present. Defaults are provided for
local usage. If environment variables are added later, they will override defaults.
"""
import os
from dataclasses import dataclass
import logging

logger = logging.getLogger("api")


def _get_stripped_env(name: str, default: str | None = None) -> str | None:
    """Read an env var and strip whitespace; return default if not set."""
    val = os.getenv(name, default if default is not None else None)
    if val is None:
        return None
    return val.strip()


@dataclass(frozen=True)
class Settings:
    # Embedding model and dimensions
    embedding_model: str = _get_stripped_env("EMBEDDING_MODEL", "text-embedding-3-small") or "text-embedding-3-small"
    embedding_dim: int = int(_get_stripped_env("EMBEDDING_DIM", "1536") or "1536")
    # FAISS index path
    faiss_index_path: str = _get_stripped_env("FAISS_INDEX_PATH", "faiss.index") or "faiss.index"
    # OpenAI model
    openai_model: str = _get_stripped_env("OPENAI_MODEL", "gpt-4o-mini") or "gpt-4o-mini"
    # OpenAI API Key (optional; handled gracefully if missing)
    # IMPORTANT: remove hardcoded default; rely on env only to avoid misleading behavior
    openai_api_key: str | None = _get_stripped_env("OPENAI_API_KEY", None)
    # Max retrieved passages for RAG
    rag_top_k: int = int(_get_stripped_env("RAG_TOP_K", "5") or "5")
    # Temperature for generation
    generation_temperature: float = float(_get_stripped_env("GEN_TEMPERATURE", "0.2") or "0.2")


SETTINGS = Settings()

# Log essential settings at import for visibility (mask API key)
try:
    key = SETTINGS.openai_api_key or ""
    masked_key = "missing"
    if key:
        # show prefix and length to help diagnose whitespace or wrong key type, but not reveal full key
        masked_key = f"{key[:5]}*** len={len(key)}"
    logger.info(
        "Config loaded: embedding_model=%s dim=%s openai_model=%s openai_api_key=%s faiss_index_path=%s",
        SETTINGS.embedding_model,
        SETTINGS.embedding_dim,
        SETTINGS.openai_model,
        masked_key,
        SETTINGS.faiss_index_path,
    )
except Exception:
    # Avoid crashing on logging issues
    pass
