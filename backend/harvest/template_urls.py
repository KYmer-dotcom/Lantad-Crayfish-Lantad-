"""
Template URLs for Harvest module
"""
from django.urls import path
from . import template_views

app_name = 'harvest'

urlpatterns = [
    path('', template_views.harvest_list, name='list'),
    path('schedule/create/', template_views.schedule_create, name='schedule_create'),
    path('record/create/', template_views.record_create, name='record_create'),
]
