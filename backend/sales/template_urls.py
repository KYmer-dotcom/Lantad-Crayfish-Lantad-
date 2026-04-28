"""
Template URLs for Sales module
"""
from django.urls import path
from . import template_views

app_name = 'sales'

urlpatterns = [
    path('', template_views.sales_list, name='list'),
    path('customer/create/', template_views.customer_create, name='customer_create'),
    path('order/create/', template_views.order_create, name='order_create'),
]
