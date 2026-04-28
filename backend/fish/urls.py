"""
FISH MODULE - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'species', views.SpeciesViewSet, basename='species')
router.register(r'batches', views.FishBatchViewSet, basename='batch')

urlpatterns = [
    path('', include(router.urls)),
]
