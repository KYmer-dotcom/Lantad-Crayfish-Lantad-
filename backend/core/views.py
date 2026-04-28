"""
Core views for dashboard and main pages
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import datetime, timedelta
import json

@login_required
def dashboard(request):
    """Main dashboard view"""
    from ponds.models import Farm, Pond
    from fish.models import FishBatch, Species
    from feed.models import FeedingLog
    from growth.models import MortalityRecord
    from harvest.models import HarvestRecord
    from sales.models import SalesOrder
    
    # Date range for 30-day stats
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
    # Basic stats
    total_farms = Farm.objects.count()
    total_ponds = Pond.objects.count()
    active_ponds = Pond.objects.filter(status='active').count()
    
    # Fish stats
    active_batches = FishBatch.objects.filter(is_active=True)
    total_fish = active_batches.aggregate(total=Sum('current_quantity'))['total'] or 0
    
    # Calculate total biomass (current_quantity * current_average_weight in kg)
    total_biomass = 0
    for batch in active_batches:
        if batch.current_quantity and batch.current_average_weight:
            total_biomass += (batch.current_quantity * float(batch.current_average_weight)) / 1000
    
    # 30-day stats
    feed_logs_30d = FeedingLog.objects.filter(feeding_time__date__gte=thirty_days_ago)
    feed_used_30d = feed_logs_30d.aggregate(total=Sum('quantity_kg'))['total'] or 0
    feeding_count = feed_logs_30d.count()
    
    mortality_30d_qs = MortalityRecord.objects.filter(record_date__gte=thirty_days_ago)
    mortality_30d = mortality_30d_qs.aggregate(total=Sum('quantity'))['total'] or 0
    mortality_events = mortality_30d_qs.count()
    
    harvest_30d_qs = HarvestRecord.objects.filter(harvest_date__gte=thirty_days_ago)
    harvest_30d = harvest_30d_qs.aggregate(total=Sum('total_weight_kg'))['total'] or 0
    harvest_count = harvest_30d_qs.count()
    
    orders_30d = SalesOrder.objects.filter(order_date__gte=thirty_days_ago)
    revenue_30d = orders_30d.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders_30d.count()
    
    # Species distribution for pie chart
    species_data = []
    species_counts = FishBatch.objects.filter(is_active=True).values('species__name').annotate(
        count=Sum('current_quantity')
    ).order_by('-count')[:10]
    
    for item in species_counts:
        if item['species__name'] and item['count']:
            species_data.append({
                'name': item['species__name'],
                'count': item['count']
            })
    
    context = {
        'stats': {
            'total_farms': total_farms,
            'total_ponds': total_ponds,
            'active_ponds': active_ponds,
            'total_fish': total_fish,
            'total_biomass': total_biomass,
            'feed_used_30d': feed_used_30d,
            'feeding_count': feeding_count,
            'mortality_30d': mortality_30d,
            'mortality_events': mortality_events,
            'harvest_30d': harvest_30d,
            'harvest_count': harvest_count,
            'revenue_30d': revenue_30d,
            'order_count': order_count,
        },
        'species_data': json.dumps(species_data),
    }
    
    return render(request, 'dashboard/dashboard.html', context)
