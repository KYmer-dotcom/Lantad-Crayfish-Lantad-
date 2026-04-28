"""
Template URLs for Ponds module
"""
from django.urls import path
from . import template_views

app_name = 'ponds'

urlpatterns = [
    path('', template_views.ponds_list, name='list'),
    path('farm/create/', template_views.farm_create, name='farm_create'),
    path('pond/create/', template_views.pond_create, name='pond_create'),
]
