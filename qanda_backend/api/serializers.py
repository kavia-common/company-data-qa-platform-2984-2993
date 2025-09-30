from rest_framework import serializers
from .models import UserProfile, Document, DocumentChunk, Embedding, Question, Answer


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ["id", "email", "display_name", "is_active", "created_at", "updated_at"]


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ["id", "document", "chunk_index", "text", "token_count", "created_at", "updated_at"]


class EmbeddingSerializer(serializers.ModelSerializer):
    chunk = DocumentChunkSerializer(read_only=True)
    chunk_id = serializers.PrimaryKeyRelatedField(
        queryset=DocumentChunk.objects.all(), source="chunk", write_only=True
    )

    class Meta:
        model = Embedding
        fields = ["id", "chunk", "chunk_id", "vector", "model", "dim", "created_at", "updated_at"]


class DocumentSerializer(serializers.ModelSerializer):
    chunks = DocumentChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Document
        fields = [
            "id", "title", "source", "source_uri", "description", "tags",
            "chunks", "created_at", "updated_at"
        ]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "user", "text", "retrieval_context", "created_at", "updated_at"]


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    question_id = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all(), source="question", write_only=True
    )

    class Meta:
        model = Answer
        fields = ["id", "question", "question_id", "answer_text", "model", "references", "meta", "created_at", "updated_at"]
