"""
Template URLs for Fish module
"""
from django.urls import path
from . import template_views

app_name = 'stock'

urlpatterns = [
    path('', template_views.products_list, name='list'),
    path('species/create/', template_views.species_create, name='species_create'),
    path('species/<int:species_id>/edit/', template_views.species_edit, name='species_edit'),
    path('species/<int:species_id>/delete/', template_views.species_delete, name='species_delete'),
    path('stock/add/', template_views.species_stock_add, name='species_stock_add'),
    path('batch/create/', template_views.batch_create, name='batch_create'),
    path('batch/<int:batch_id>/update/', template_views.batch_update, name='batch_update'),
]
