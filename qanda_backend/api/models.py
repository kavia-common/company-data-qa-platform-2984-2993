from django.db import models


class TimestampedModel(models.Model):
    """Abstract base model with created/updated timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        abstract = True


class UserProfile(TimestampedModel):
    """
    Represents an end user or service user for the Q&A system.
    Minimal fields for demo use; can be linked to auth.User if needed later.
    """
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=120, blank=True, default="")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name or self.email


class Document(TimestampedModel):
    """
    Stores document-level metadata. Content is broken into chunks stored in DocumentChunk.
    """
    SOURCE_CHOICES = (
        ("manual", "Manual Upload"),
        ("seed", "Seed Data"),
        ("url", "Web URL"),
        ("other", "Other"),
    )
    title = models.CharField(max_length=255)
    source = models.CharField(max_length=32, choices=SOURCE_CHOICES, default="manual")
    source_uri = models.TextField(blank=True, default="")
    description = models.TextField(blank=True, default="")
    tags = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.title


class DocumentChunk(TimestampedModel):
    """
    Stores chunked content for a document. Each chunk can have an embedding vector.
    """
    document = models.ForeignKey(Document, related_name="chunks", on_delete=models.CASCADE)
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()
    token_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("document", "chunk_index")
        ordering = ["document_id", "chunk_index"]

    def __str__(self):
        return f"{self.document_id}:{self.chunk_index}"


class Embedding(TimestampedModel):
    """
    Stores embeddings for a chunk. We keep the vector as a list[float] to remain DB agnostic.
    FAISS will be used for actual vector retrieval; DB is for metadata and rebuilds.
    """
    chunk = models.OneToOneField(DocumentChunk, related_name="embedding", on_delete=models.CASCADE)
    vector = models.JSONField()  # list of floats
    model = models.CharField(max_length=128, default="text-embedding-3-small")
    dim = models.PositiveIntegerField(default=1536)

    def __str__(self):
        return f"Embedding(chunk={self.chunk_id}, dim={self.dim})"


class Question(TimestampedModel):
    """
    A user question asked to the system.
    """
    user = models.ForeignKey(UserProfile, null=True, blank=True, on_delete=models.SET_NULL, related_name="questions")
    text = models.TextField()
    # optional serialized retrieval context for debugging
    retrieval_context = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Q{self.id}: {self.text[:40]}..."


class Answer(TimestampedModel):
    """
    AI generated answer with references to supporting chunks.
    """
    question = models.OneToOneField(Question, related_name="answer", on_delete=models.CASCADE)
    answer_text = models.TextField()
    model = models.CharField(max_length=128, default="gpt-4o-mini")
    # top_k retrieved passages and scores: [{chunk_id, score, text, document_id, document_title}]
    references = models.JSONField(default=list, blank=True)
    # raw LLM call info for traceability
    meta = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Ans to Q{self.question_id}"
