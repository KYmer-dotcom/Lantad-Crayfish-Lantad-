"""
Template URLs for Feed module
"""
from django.urls import path
from django.views.generic import RedirectView
from . import template_views

app_name = 'feed'

urlpatterns = [
    path('', template_views.feed_list, name='list'),
    path('supplies/', RedirectView.as_view(pattern_name='feed:list', permanent=False)),
    path('stock/add/', template_views.feed_stock_add, name='feed_stock_add'),
    path('types/add/', template_views.feed_type_add, name='feed_type_add'),
    path('types/<int:feed_type_id>/edit/', template_views.feed_type_edit, name='feed_type_edit'),
    path('types/<int:feed_type_id>/delete/', template_views.feed_type_delete, name='feed_type_delete'),
    path('types/<int:feed_id>/add-sack/', template_views.feed_add_sack, name='feed_add_sack'),
    path('sacks/<int:sack_id>/delete/', template_views.feed_delete_sack, name='feed_delete_sack'),
    path('feeding-log/create/', template_views.feeding_log_create, name='feeding_log_create'),
]

