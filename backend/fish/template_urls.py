"""
Template URLs for Fish module
"""
from django.urls import path
from . import template_views

app_name = 'fish'

urlpatterns = [
    path('', template_views.fish_list, name='list'),
    path('species/create/', template_views.species_create, name='species_create'),
    path('batch/create/', template_views.batch_create, name='batch_create'),
]
