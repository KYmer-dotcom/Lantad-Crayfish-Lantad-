"""
Template views for Analytics module
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
import json

from ponds.models import Pond
from fish.models import FishBatch
from harvest.models import HarvestRecord
from sales.models import SalesOrder
from .models import HarvestForecast, SalesForecast


@login_required
def analytics_dashboard(request):
    """Analytics dashboard with KPIs, charts, and forecasts"""
    
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # KPI Summary Cards
    active_ponds = Pond.objects.filter(status='active').count()
    
    active_batches = FishBatch.objects.filter(is_active=True)
    total_fish_stock = active_batches.aggregate(total=Sum('current_quantity'))['total'] or 0
    total_biomass = sum(
        batch.current_quantity * float(batch.current_average_weight) / 1000
        for batch in active_batches
    )
    
    # Monthly Revenue
    monthly_revenue = SalesOrder.objects.filter(
        order_date__gte=thirty_days_ago,
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Monthly Harvest
    monthly_harvest = HarvestRecord.objects.filter(
        harvest_date__gte=thirty_days_ago
    ).aggregate(total=Sum('total_weight_kg'))['total'] or 0
    
    # Production Overview Chart Data
    production_data = {
        'fish_stock': total_fish_stock,
        'biomass_kg': round(float(total_biomass), 2),
        'harvested_kg': round(float(monthly_harvest), 2)
    }
    
    # Sales Performance Chart Data
    sales_stats = SalesOrder.objects.filter(
        order_date__gte=thirty_days_ago,
        status='completed'
    ).aggregate(
        total_revenue=Sum('total_amount'),
        total_orders=Count('id')
    )
    
    sales_data = {
        'orders': sales_stats['total_orders'] or 0,
        'revenue_k': round(float(sales_stats['total_revenue'] or 0) / 1000, 2)
    }
    
    # Harvest Forecasts
    harvest_forecasts = HarvestForecast.objects.select_related(
        'fish_batch'
    ).order_by('predicted_harvest_date')[:10]
    
    # Sales Forecasts
    sales_forecasts = SalesForecast.objects.select_related(
        'species'
    ).order_by('period_start')[:10]
    
    context = {
        # KPI Summary
        'active_ponds': active_ponds,
        'total_fish_stock': total_fish_stock,
        'monthly_revenue': monthly_revenue,
        'monthly_harvest': monthly_harvest,
        'total_biomass': total_biomass,
        
        # Chart Data
        'production_data': json.dumps(production_data),
        'sales_data': json.dumps(sales_data),
        
        # Forecasts
        'harvest_forecasts': harvest_forecasts,
        'sales_forecasts': sales_forecasts,
    }
    
    return render(request, 'analytics/dashboard.html', context)
