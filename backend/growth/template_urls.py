"""
Template URLs for Growth module
"""
from django.urls import path
from . import template_views

app_name = 'growth'

urlpatterns = [
    path('', template_views.growth_list, name='list'),
    path('sample/create/', template_views.sample_create, name='sample_create'),
    path('mortality/create/', template_views.mortality_create, name='mortality_create'),
]
