"""
URL configuration for core project.
API Endpoints and Template Views organized by module.
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # ============================================================
    # TEMPLATE VIEWS - Django Frontend
    # ============================================================
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Module Pages
    path('ponds/', include('ponds.template_urls')),
    path('fish/', include('fish.template_urls')),
    path('feed/', include('feed.template_urls')),
    path('growth/', include('growth.template_urls')),
    path('harvest/', include('harvest.template_urls')),
    path('sales/', include('sales.template_urls')),
    path('analytics/', include('analytics.template_urls')),
    
    # ============================================================
    # API ENDPOINTS - REST API (kept for compatibility)
    # ============================================================
    
    # ACCOUNTS MODULE - Authentication & User Management
    path('api/auth/', include('accounts.urls')),
    
    # PONDS MODULE - Pond and Farm Management
    path('api/ponds/', include(('ponds.urls', 'ponds_api'))),
    
    # FISH MODULE - Fish Stocking and Classification
    path('api/fish/', include(('fish.urls', 'fish_api'))),
    
    # FEED MODULE - Feed Consumption Tracking
    path('api/feed/', include(('feed.urls', 'feed_api'))),
    
    # GROWTH MODULE - Growth and Mortality Monitoring
    path('api/growth/', include(('growth.urls', 'growth_api'))),
    
    # HARVEST MODULE - Harvest Management
    path('api/harvest/', include(('harvest.urls', 'harvest_api'))),
    
    # SALES MODULE - Sales and Distribution
    path('api/sales/', include(('sales.urls', 'sales_api'))),
    
    # ANALYTICS MODULE - Data Analytics and Forecasting
    path('api/analytics/', include(('analytics.urls', 'analytics_api'))),
]
