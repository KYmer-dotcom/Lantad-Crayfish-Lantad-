"""
HARVEST MODULE - URL Configuration
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'schedules', views.HarvestScheduleViewSet, basename='harvest-schedule')
router.register(r'records', views.HarvestRecordViewSet, basename='harvest-record')

urlpatterns = [
    path('', include(router.urls)),
]
