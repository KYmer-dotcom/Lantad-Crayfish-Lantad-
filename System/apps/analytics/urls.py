"""
ANALYTICS MODULE - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'harvest-forecasts', views.HarvestForecastViewSet, basename='harvest-forecast')
router.register(r'sales-forecasts', views.SalesForecastViewSet, basename='sales-forecast')
router.register(r'metrics', views.PerformanceMetricViewSet, basename='metric')

urlpatterns = [
    path('', include(router.urls)),
]
