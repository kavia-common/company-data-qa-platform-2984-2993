from django.core.management.base import BaseCommand
from api.models import Document, DocumentChunk
from api.services.tokenizer import count_tokens
from api.services.embeddings import embed_texts
from api.services.faiss_index import upsert_chunk_embedding
from api.services.config import SETTINGS


SEED_DOCS = [
    {
        "title": "Company Handbook - Mission and Values",
        "description": "Overview of mission, values, and culture.",
        "source": "seed",
        "chunks": [
            "Our mission is to empower customers through data-driven insights and seamless digital experiences.",
            "Core values include customer obsession, integrity, continuous learning, and collaboration.",
        ],
    },
    {
        "title": "HR Policies - PTO and Holidays",
        "description": "HR policies related to paid time off and observed holidays.",
        "source": "seed",
        "chunks": [
            "Employees accrue PTO monthly and can carry over limited hours to the next year.",
            "Observed company holidays include New Year's Day, Independence Day, Thanksgiving, and Christmas.",
        ],
    },
]


class Command(BaseCommand):
    help = "Seeds demo documents and creates embeddings for them."

    def handle(self, *args, **kwargs):
        for doc_spec in SEED_DOCS:
            doc, _ = Document.objects.get_or_create(
                title=doc_spec["title"],
                defaults={
                    "description": doc_spec["description"],
                    "source": doc_spec["source"],
                    "tags": [],
                },
            )
            for idx, text in enumerate(doc_spec["chunks"]):
                chunk, _ = DocumentChunk.objects.get_or_create(
                    document=doc,
                    chunk_index=idx,
                    defaults={"text": text, "token_count": count_tokens(text)},
                )
                vec = embed_texts([text])[0]
                upsert_chunk_embedding(chunk, vec, SETTINGS.embedding_model, SETTINGS.embedding_dim)
        self.stdout.write(self.style.SUCCESS("Seeded demo data and built embeddings."))
