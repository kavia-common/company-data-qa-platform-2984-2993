# Q&A Backend

Django REST backend for company data Q&A with RAG workflow, FAISS, and OpenAI.

Environment setup:
- Place the .env file in qanda_backend/. The settings loader and entrypoints (manage.py, ASGI/WSGI) load this file at startup.
- Variables:
  - OPENAI_API_KEY=sk-...
  - OPENAI_MODEL (default gpt-4o-mini)
  - EMBEDDING_MODEL (default text-embedding-3-small)
  - EMBEDDING_DIM (default 1536)
  - FAISS_INDEX_PATH (default faiss.index)
  - RAG_TOP_K (default 5)
  - GEN_TEMPERATURE (default 0.2)

Key features:
- Document management with chunking
- Embedding generation with OpenAI or deterministic fallback
- FAISS vector index for retrieval
- RAG Q&A endpoint with answer generation (OpenAI or fallback)
- OpenAPI docs at /docs

Run migrations:
- python manage.py makemigrations
- python manage.py migrate

Seed demo data:
- python manage.py seed_demo_data

OpenAPI JSON:
- python manage.py generate_openapi

Environment variables (optional):
- OPENAI_API_KEY
- OPENAI_MODEL (default gpt-4o-mini)
- EMBEDDING_MODEL (default text-embedding-3-small)
- EMBEDDING_DIM (default 1536)
- FAISS_INDEX_PATH (default faiss.index)
- RAG_TOP_K (default 5)
- GEN_TEMPERATURE (default 0.2)
