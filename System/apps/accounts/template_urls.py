"""
Template URLs for Accounts module
"""
from django.urls import path
from . import template_views

app_name = 'accounts'

urlpatterns = [
    path('', template_views.user_list, name='list'),
    path('customers/<int:customer_id>/remove/', template_views.customer_remove, name='customer_remove'),
]
