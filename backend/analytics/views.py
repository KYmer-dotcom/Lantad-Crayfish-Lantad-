"""
ANALYTICS MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import HarvestForecast, SalesForecast, PerformanceMetric
from .serializers import HarvestForecastSerializer, SalesForecastSerializer, PerformanceMetricSerializer

from ponds.models import Pond, Farm
from fish.models import FishBatch, Species
from feed.models import FeedingLog
from growth.models import MortalityRecord
from harvest.models import HarvestRecord
from sales.models import SalesOrder


class HarvestForecastViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Harvest Forecasts.
    """
    
    queryset = HarvestForecast.objects.select_related('fish_batch').all()
    serializer_class = HarvestForecastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['forecast_date', 'predicted_harvest_date', 'created_at']


class SalesForecastViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Sales Forecasts.
    """
    
    queryset = SalesForecast.objects.select_related('species').all()
    serializer_class = SalesForecastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['forecast_date', 'period_start', 'created_at']


class PerformanceMetricViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Performance Metrics with Dashboard data.
    """
    
    queryset = PerformanceMetric.objects.all()
    serializer_class = PerformanceMetricSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['metric_date', 'created_at']
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get real-time dashboard data."""
        
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Pond Statistics
        total_farms = Farm.objects.filter(is_active=True).count()
        total_ponds = Pond.objects.count()
        active_ponds = Pond.objects.filter(status='active').count()
        
        # Fish Statistics
        active_batches = FishBatch.objects.filter(is_active=True)
        total_fish = active_batches.aggregate(total=Sum('current_quantity'))['total'] or 0
        total_biomass = sum(
            batch.current_quantity * float(batch.current_average_weight) / 1000
            for batch in active_batches
        )
        
        # Feed Statistics (last 30 days)
        feed_stats = FeedingLog.objects.filter(
            feeding_time__date__gte=thirty_days_ago
        ).aggregate(
            total_feed=Sum('quantity_kg'),
            total_feedings=Count('id')
        )
        
        # Mortality Statistics (last 30 days)
        mortality_stats = MortalityRecord.objects.filter(
            record_date__gte=thirty_days_ago
        ).aggregate(
            total_mortality=Sum('quantity'),
            mortality_events=Count('id')
        )
        
        # Harvest Statistics (last 30 days)
        harvest_stats = HarvestRecord.objects.filter(
            harvest_date__gte=thirty_days_ago
        ).aggregate(
            total_harvest_kg=Sum('total_weight_kg'),
            total_harvests=Count('id')
        )
        
        # Sales Statistics (last 30 days)
        sales_stats = SalesOrder.objects.filter(
            order_date__gte=thirty_days_ago,
            status='completed'
        ).aggregate(
            total_revenue=Sum('total_amount'),
            total_orders=Count('id')
        )
        
        # Species Distribution
        species_distribution = []
        for species in Species.objects.all():
            count = FishBatch.objects.filter(
                species=species, is_active=True
            ).aggregate(total=Sum('current_quantity'))['total'] or 0
            if count > 0:
                species_distribution.append({
                    'species': species.name,
                    'count': count
                })
        
        return Response({
            'summary': {
                'total_farms': total_farms,
                'total_ponds': total_ponds,
                'active_ponds': active_ponds,
                'total_fish': total_fish,
                'total_biomass_kg': round(total_biomass, 2),
            },
            'feed_30_days': {
                'total_feed_kg': float(feed_stats['total_feed'] or 0),
                'total_feedings': feed_stats['total_feedings'] or 0,
            },
            'mortality_30_days': {
                'total_mortality': mortality_stats['total_mortality'] or 0,
                'mortality_events': mortality_stats['mortality_events'] or 0,
            },
            'harvest_30_days': {
                'total_harvest_kg': float(harvest_stats['total_harvest_kg'] or 0),
                'total_harvests': harvest_stats['total_harvests'] or 0,
            },
            'sales_30_days': {
                'total_revenue': float(sales_stats['total_revenue'] or 0),
                'total_orders': sales_stats['total_orders'] or 0,
            },
            'species_distribution': species_distribution,
        })
