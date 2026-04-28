"""
GROWTH MODULE - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'samples', views.GrowthSampleViewSet, basename='growth-sample')
router.register(r'mortality', views.MortalityRecordViewSet, basename='mortality')

urlpatterns = [
    path('', include(router.urls)),
]
