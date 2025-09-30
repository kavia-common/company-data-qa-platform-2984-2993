"""
FAISS index manager for chunk embeddings.

We persist a FAISS index on disk for efficient similarity search and keep
a mapping between index positions and chunk IDs.
"""
from __future__ import annotations
import os
import json
from typing import List, Tuple, Optional

import faiss  # type: ignore
import numpy as np  # type: ignore

from django.db import transaction
from ..models import Embedding, DocumentChunk
from .config import SETTINGS


class FaissIndex:
    """
    PUBLIC_INTERFACE
    Manages a FAISS index for cosine similarity search over chunk embeddings.
    """
    def __init__(self, dim: int, index_path: str, map_path: Optional[str] = None):
        self.dim = dim
        self.index_path = index_path
        self.map_path = map_path or f"{index_path}.map.json"
        self.index = None  # type: ignore
        self.id_map: List[int] = []
        self._load_or_create()

    def _create_index(self):
        # Use IndexFlatIP for cosine similarity with normalized vectors.
        self.index = faiss.IndexFlatIP(self.dim)

    def _load_or_create(self):
        if os.path.exists(self.index_path) and os.path.exists(self.map_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.map_path, "r") as f:
                self.id_map = json.load(f)
        else:
            self._create_index()
            self._persist()

    def _persist(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.map_path, "w") as f:
            json.dump(self.id_map, f)

    def _normalize(self, vecs: np.ndarray) -> np.ndarray:
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms

    # PUBLIC_INTERFACE
    def rebuild_from_db(self):
        """
        Rebuild the FAISS index from Embedding records in the database.
        """
        vectors: List[List[float]] = []
        self.id_map = []
        for emb in Embedding.objects.all().select_related("chunk"):
            vectors.append(emb.vector)
            self.id_map.append(emb.chunk_id)
        self._create_index()
        if vectors:
            arr = np.array(vectors, dtype="float32")
            arr = self._normalize(arr)
            self.index.add(arr)
        self._persist()

    # PUBLIC_INTERFACE
    def add_embeddings(self, chunk_ids: List[int], vectors: List[List[float]]):
        """
        Add new vectors to the index and extend the id_map accordingly.
        """
        if not vectors:
            return
        arr = np.array(vectors, dtype="float32")
        arr = self._normalize(arr)
        self.index.add(arr)
        self.id_map.extend(chunk_ids)
        self._persist()

    # PUBLIC_INTERFACE
    def search(self, query_vector: List[float], top_k: int = 5) -> List[Tuple[int, float]]:
        """
        Search the index with a query vector and return a list of (chunk_id, score) pairs.
        """
        if self.index.ntotal == 0:
            return []
        q = np.array([query_vector], dtype="float32")
        q = self._normalize(q)
        scores, idx = self.index.search(q, top_k)
        results: List[Tuple[int, float]] = []
        for i, score in zip(idx[0], scores[0]):
            if i == -1:
                continue
            chunk_id = self.id_map[i]
            results.append((chunk_id, float(score)))
        return results


# Singleton helper
_faiss_instance: Optional[FaissIndex] = None


# PUBLIC_INTERFACE
def get_faiss_index() -> FaissIndex:
    """
    Provides a singleton FAISS index bound to settings.
    """
    global _faiss_instance
    if _faiss_instance is None:
        _faiss_instance = FaissIndex(dim=SETTINGS.embedding_dim, index_path=SETTINGS.faiss_index_path)
    return _faiss_instance


# PUBLIC_INTERFACE
def ensure_index_in_sync():
    """
    Ensures FAISS index is built from DB if empty or mismatched.
    """
    idx = get_faiss_index()
    # simple heuristic: rebuild if counts mismatch
    if idx.index.ntotal != Embedding.objects.count():
        idx.rebuild_from_db()


# PUBLIC_INTERFACE
def upsert_chunk_embedding(chunk: DocumentChunk, vector: List[float], model: str, dim: int):
    """
    Create or update embedding record; update FAISS index by rebuilding or adding.
    """
    with transaction.atomic():
        emb, created = Embedding.objects.update_or_create(
            chunk=chunk, defaults={"vector": vector, "model": model, "dim": dim}
        )
    # Simple approach: rebuild if updated existing; append if created
    idx = get_faiss_index()
    if created:
        idx.add_embeddings([chunk.id], [vector])
    else:
        idx.rebuild_from_db()
