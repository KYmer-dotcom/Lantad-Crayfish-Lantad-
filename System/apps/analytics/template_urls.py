"""
Template URLs for Analytics module
"""
from django.urls import path
from . import template_views

app_name = 'analytics'

urlpatterns = [
    path('', template_views.analytics_dashboard, name='dashboard'),
    path('reports/', template_views.reports, name='reports'),
]
