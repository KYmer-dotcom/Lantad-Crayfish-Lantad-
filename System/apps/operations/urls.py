"""
PONDS MODULE - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'farms', views.FarmViewSet, basename='farm')
router.register(r'ponds', views.PondViewSet, basename='pond')

urlpatterns = [
    path('', include(router.urls)),
]
