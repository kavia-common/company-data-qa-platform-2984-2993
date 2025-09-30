from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import UserProfile, Document, DocumentChunk
from .serializers import (
    UserProfileSerializer,
    DocumentSerializer,
    QuestionSerializer,
    AnswerSerializer,
)
from .services.tokenizer import count_tokens
from .services.embeddings import embed_texts
from .services.faiss_index import upsert_chunk_embedding
from .services.rag import ask_question
from .services.config import SETTINGS


@swagger_auto_schema(
    method="get",
    operation_summary="Health check",
    operation_description="Simple endpoint to verify the server is up.",
    responses={200: openapi.Response(description="Server health", schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={"message": openapi.Schema(type=openapi.TYPE_STRING)},
    ))},
    tags=["System"],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    """
    PUBLIC_INTERFACE
    Health check endpoint.

    Returns:
        JSON object with message confirming server status.
    """
    return Response({"message": "Server is up!"})


class UserProfileViewSet(mixins.CreateModelMixin,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    PUBLIC_INTERFACE
    CRUD operations for user profiles.
    """
    queryset = UserProfile.objects.all().order_by("-created_at")
    serializer_class = UserProfileSerializer

    @swagger_auto_schema(operation_summary="List users", tags=["Users"])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Create user", tags=["Users"])
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Retrieve user", tags=["Users"])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(operation_summary="Update user", tags=["Users"])
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    PUBLIC_INTERFACE
    Manage documents and their content chunks.
    """
    queryset = Document.objects.all().order_by("-created_at")
    serializer_class = DocumentSerializer

    @swagger_auto_schema(operation_summary="Upload or create a document", tags=["Documents"])
    def create(self, request, *args, **kwargs):
        """
        Create a Document. Optionally include "chunks": [{text: str, chunk_index?: int}]
        If chunks are provided, embeddings will be created.
        """
        payload = request.data
        chunks = payload.pop("chunks", [])
        serializer = self.get_serializer(data=payload)
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            doc = serializer.save()
            for idx, ch in enumerate(chunks):
                text = ch.get("text", "")
                chunk_index = ch.get("chunk_index", idx)
                chunk = DocumentChunk.objects.create(
                    document=doc,
                    chunk_index=chunk_index,
                    text=text,
                    token_count=count_tokens(text),
                )
                vec = embed_texts([text])[0]
                upsert_chunk_embedding(chunk, vec, SETTINGS.embedding_model, SETTINGS.embedding_dim)
            headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(doc).data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(operation_summary="Add chunk to a document", tags=["Documents"])
    def partial_update(self, request, *args, **kwargs):
        """
        Partial update: supports adding chunks via {"add_chunk": {"text": "...", "chunk_index": optional}}
        """
        doc = self.get_object()
        add_chunk = request.data.get("add_chunk")
        if add_chunk:
            text = add_chunk.get("text", "")
            chunk_index = add_chunk.get("chunk_index", doc.chunks.count())
            chunk = DocumentChunk.objects.create(
                document=doc, chunk_index=chunk_index, text=text, token_count=count_tokens(text)
            )
            vec = embed_texts([text])[0]
            upsert_chunk_embedding(chunk, vec, SETTINGS.embedding_model, SETTINGS.embedding_dim)
        return Response(self.get_serializer(doc).data, status=status.HTTP_200_OK)


class EmbeddingView(APIView):
    """
    PUBLIC_INTERFACE
    Generate embeddings for arbitrary input texts. Useful to test embedding integration.
    """
    @swagger_auto_schema(
        operation_summary="Generate embeddings",
        operation_description="Returns embedding vectors for a list of texts. If OpenAI key isn't set, returns deterministic pseudo-embeddings.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"texts": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING))},
            required=["texts"],
        ),
        responses={200: openapi.Response(description="Embedding vectors")},
        tags=["Embeddings"],
    )
    def post(self, request):
        texts = request.data.get("texts", [])
        if not isinstance(texts, list):
            return Response({"detail": "texts must be a list"}, status=400)
        vectors = embed_texts([str(t) for t in texts])
        return Response({"vectors": vectors, "dim": SETTINGS.embedding_dim, "model": SETTINGS.embedding_model})


class QAView(APIView):
    """
    PUBLIC_INTERFACE
    Ask a question using RAG over the indexed company documents.
    """
    @swagger_auto_schema(
        operation_id="ask_question",
        operation_summary="Ask a question",
        operation_description="Runs a RAG workflow: retrieve relevant chunks with FAISS and generate an answer via OpenAI or fallback.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={"question": openapi.Schema(type=openapi.TYPE_STRING), "user_id": openapi.Schema(type=openapi.TYPE_INTEGER)},
            required=["question"],
        ),
        responses={200: openapi.Response(description="Answer with references")},
        tags=["Q&A"],
    )
    def post(self, request):
        text = request.data.get("question", "").strip()
        if not text:
            return Response({"detail": "question is required"}, status=400)
        user = None
        user_id = request.data.get("user_id")
        if user_id:
            user = get_object_or_404(UserProfile, pk=user_id)
        result = ask_question(text, user=user)
        return Response(
            {
                "question": QuestionSerializer(result["question"]).data,
                "answer": AnswerSerializer(result["answer"]).data,
            }
        )
