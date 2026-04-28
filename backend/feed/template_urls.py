"""
Template URLs for Feed module
"""
from django.urls import path
from . import template_views

app_name = 'feed'

urlpatterns = [
    path('', template_views.feed_list, name='list'),
    path('feed-type/create/', template_views.feed_type_create, name='feed_type_create'),
    path('feeding-log/create/', template_views.feeding_log_create, name='feeding_log_create'),
]
