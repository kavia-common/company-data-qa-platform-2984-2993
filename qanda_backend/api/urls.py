from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import health, UserProfileViewSet, DocumentViewSet, EmbeddingView, QAView

router = DefaultRouter()
router.register(r'users', UserProfileViewSet, basename='users')
router.register(r'documents', DocumentViewSet, basename='documents')

urlpatterns = [
    path('health/', health, name='Health'),
    path('', include(router.urls)),
    path('embeddings/', EmbeddingView.as_view(), name='embeddings'),
    path('qa/', QAView.as_view(), name='qa'),
]
