"""
Template URLs for Ponds module
"""
from django.urls import path
from . import template_views

app_name = 'ponds'

urlpatterns = [
    path('', template_views.ponds_list, name='list'),
    path('map/', template_views.pond_geomap, name='geomap'),
    path('farm/create/', template_views.farm_create, name='farm_create'),
    path('pond/create/', template_views.pond_create, name='pond_create'),
    path('pond/<int:pond_id>/edit/', template_views.pond_edit, name='pond_edit'),
    path('farm/<int:farm_id>/remove/', template_views.farm_remove, name='farm_remove'),
    path('pond/<int:pond_id>/remove/', template_views.pond_remove, name='pond_remove'),
    path('operations/', template_views.operations_data, name='operations_data'),
    path('operations/record/', template_views.record_operations, name='record_operations'),
]
