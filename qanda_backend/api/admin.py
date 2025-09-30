from django.contrib import admin
from .models import UserProfile, Document, DocumentChunk, Embedding, Question, Answer


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "display_name", "is_active", "created_at", "updated_at")
    search_fields = ("email", "display_name")


class DocumentChunkInline(admin.TabularInline):
    model = DocumentChunk
    extra = 0
    readonly_fields = ("token_count",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "source", "created_at", "updated_at")
    search_fields = ("title", "description")
    inlines = [DocumentChunkInline]


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ("id", "chunk", "model", "dim", "created_at")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "text", "created_at")
    search_fields = ("text",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("id", "question", "model", "created_at")
