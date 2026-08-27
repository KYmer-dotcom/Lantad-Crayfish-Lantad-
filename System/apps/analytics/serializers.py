"""
ANALYTICS MODULE - Serializers
"""

from rest_framework import serializers
from .models import HarvestForecast, SalesForecast, PerformanceMetric


class HarvestForecastSerializer(serializers.ModelSerializer):
    """Serializer for HarvestForecast model."""
    
    stock_batch_code = serializers.CharField(source='stock_batch.batch_code', read_only=True)
    
    class Meta:
        model = HarvestForecast
        fields = ['id', 'stock_batch', 'stock_batch_code', 'forecast_date',
                  'predicted_harvest_date', 'predicted_weight', 'predicted_quantity',
                  'predicted_total_yield', 'confidence_level', 'algorithm_used',
                  'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SalesForecastSerializer(serializers.ModelSerializer):
    """Serializer for SalesForecast model."""
    
    species_name = serializers.CharField(source='species.name', read_only=True)
    accuracy = serializers.ReadOnlyField()
    
    class Meta:
        model = SalesForecast
        fields = ['id', 'forecast_date', 'period_start', 'period_end',
                  'predicted_demand_kg', 'predicted_revenue', 'species', 'species_name',
                  'confidence_level', 'algorithm_used', 'actual_demand_kg',
                  'actual_revenue', 'accuracy', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class PerformanceMetricSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceMetric model."""
    
    metric_type_display = serializers.CharField(source='get_metric_type_display', read_only=True)
    
    class Meta:
        model = PerformanceMetric
        fields = ['id', 'metric_date', 'metric_type', 'metric_type_display',
                  'total_ponds_active', 'total_fish_stock', 'total_biomass_kg',
                  'total_feed_used_kg', 'feed_cost', 'total_mortality', 'mortality_rate',
                  'total_harvest_kg', 'harvest_value', 'total_sales', 'total_orders',
                  'created_at']
        read_only_fields = ['id', 'created_at']
