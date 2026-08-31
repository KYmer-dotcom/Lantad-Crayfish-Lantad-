"""
URL configuration for core project.
API Endpoints and Template Views organized by module.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ============================================================
    # TEMPLATE VIEWS - Django Frontend
    # ============================================================
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('customer/', lambda request: redirect('sales:customer_portal'), name='customer_home'),
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('logout/', views.app_logout, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('inventory/', views.inventory_overview, name='inventory'),
    path('delivery/', lambda request: redirect('sales:delivery_list'), name='delivery'),
    path('track-order/', lambda request: redirect('sales:delivery_track'), name='track_order_root'),
    path('delivery/track/', lambda request: redirect('sales:delivery_track')),
    path('delivery-logs/', lambda request: redirect('sales:delivery_logs'), name='delivery_logs_root'),
    path('delivery/logs/', lambda request: redirect('sales:delivery_logs')),
    path('notifications/', views.notifications, name='notifications'),
    
    # Module Pages
    path('operations/', include(('apps.operations.template_urls', 'ponds'), namespace='operations')),
    path('products/', include('apps.stock.template_urls')),
    path('feed/', include('apps.feed.template_urls')),
    path('harvest/', include('apps.harvest.template_urls')),
    path('sales/', include('apps.sales.template_urls')),
    path('analytics/', include('apps.analytics.template_urls')),
    path('accounts/', include('apps.accounts.template_urls')),
    
    # ============================================================
    # API ENDPOINTS - REST API (REMOVED)
    # ============================================================
]

# Serve media files in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
