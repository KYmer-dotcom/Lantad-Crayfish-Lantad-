"""
FEED MODULE - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'types', views.FeedTypeViewSet, basename='feed-type')
router.register(r'inventory', views.FeedInventoryViewSet, basename='feed-inventory')
router.register(r'logs', views.FeedingLogViewSet, basename='feeding-log')

urlpatterns = [
    path('', include(router.urls)),
]
