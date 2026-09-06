from rest_framework import serializers
from .models import HarvestForecast, SalesForecast


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
