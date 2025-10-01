"""
RAG pipeline orchestration:
- embed the question
- retrieve top-k chunks with FAISS
- construct context
- call LLM
- persist Question and Answer
"""
from __future__ import annotations
from typing import Dict, List

from django.db import transaction

from ..models import Question, Answer, DocumentChunk, UserProfile
from .config import SETTINGS
from .embeddings import embed_texts
from .faiss_index import ensure_index_in_sync, get_faiss_index
from .openai_client import generate_answer


# PUBLIC_INTERFACE
def ask_question(text: str, user: UserProfile | None = None) -> Dict:
    """
    Execute a RAG workflow to answer a user's question.

    Args:
        text: question text
        user: optional UserProfile

    Returns:
        dict: question, answer, references
    """
    ensure_index_in_sync()
    q_vec = embed_texts([text])[0]
    results = get_faiss_index().search(q_vec, top_k=SETTINGS.rag_top_k)

    references: List[Dict] = []
    context_snippets: List[str] = []

    chunks_by_id = {c.id: c for c in DocumentChunk.objects.filter(id__in=[cid for cid, _ in results]).select_related("document")}
    for chunk_id, score in results:
        chunk = chunks_by_id.get(chunk_id)
        if not chunk:
            continue
        references.append(
            {
                "chunk_id": chunk.id,
                "score": score,
                "text": chunk.text,
                "document_id": chunk.document_id,
                "document_title": chunk.document.title,
            }
        )
        context_snippets.append(chunk.text)

    gen = generate_answer(text, context_snippets)
    with transaction.atomic():
        q = Question.objects.create(
            user=user,
            text=text,
            retrieval_context={
                "top_k": SETTINGS.rag_top_k,
                "retrieved": [
                    {"chunk_id": r["chunk_id"], "score": r["score"], "document_id": r["document_id"]}
                    for r in references
                ],
            },
        )
        a = Answer.objects.create(
            question=q,
            answer_text=gen["text"],
            model=gen["model"],
            references=references,
            meta=gen.get("meta", {}),
        )
    return {"question": q, "answer": a}
