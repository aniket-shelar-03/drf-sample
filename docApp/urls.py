from django.urls import path, include
from .views import BookModelViewSet, AuthorModelViewSet

from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r"books", BookModelViewSet, basename="book")
router.register(r"authors", AuthorModelViewSet, basename="author")

urlpatterns = [
    path("", include(router.urls)),
]