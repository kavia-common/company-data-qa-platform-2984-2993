"""
Configuration utilities.

No environment variables are assumed to be present. Defaults are provided for
local usage. If environment variables are added later, they will override defaults.
"""
import os
from dataclasses import dataclass
import logging

logger = logging.getLogger("api")


@dataclass(frozen=True)
class Settings:
    # Embedding model and dimensions
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "1536"))
    # FAISS index path
    faiss_index_path: str = os.getenv("FAISS_INDEX_PATH", "faiss.index")
    # OpenAI model
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    # OpenAI API Key (optional in this scaffold; handled gracefully if missing)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    # Max retrieved passages for RAG
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "5"))
    # Temperature for generation
    generation_temperature: float = float(os.getenv("GEN_TEMPERATURE", "0.2"))


SETTINGS = Settings()

# Log essential settings at import for visibility (mask API key)
try:
    masked_key = "set" if SETTINGS.openai_api_key else "missing"
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
