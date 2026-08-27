"""
FISH MODULE - Serializers
"""

from rest_framework import serializers
from .models import Species, StockBatch


class SpeciesSerializer(serializers.ModelSerializer):
    """Serializer for Species model."""
    
    class Meta:
        model = Species
        fields = ['id', 'name', 'category', 'scientific_name', 'description', 'average_growth_rate',
                  'market_weight_g', 'optimal_temperature_min', 'optimal_temperature_max',
                  'optimal_ph_min', 'optimal_ph_max', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockBatchSerializer(serializers.ModelSerializer):
    """Serializer for StockBatch model."""
    
    pond_name = serializers.CharField(source='pond.name', read_only=True)
    species_name = serializers.CharField(source='species.name', read_only=True)
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    mortality_count = serializers.ReadOnlyField()
    mortality_rate = serializers.ReadOnlyField()
    total_biomass = serializers.ReadOnlyField()
    stocked_by_name = serializers.CharField(source='stocked_by.username', read_only=True)
    
    class Meta:
        model = StockBatch
        fields = ['id', 'pond', 'pond_name', 'species', 'species_name', 'batch_code',
                  'stocking_date', 'initial_quantity', 'current_quantity',
                  'initial_average_weight', 'current_average_weight', 'stage', 'stage_display',
                  'supplier', 'cost_per_unit', 'is_active', 'notes',
                  'stocked_by', 'stocked_by_name', 'mortality_count', 'mortality_rate',
                  'total_biomass', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockBatchCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating StockBatch."""
    
    class Meta:
        model = StockBatch
        fields = ['pond', 'species', 'batch_code', 'stocking_date', 'initial_quantity',
                  'initial_average_weight', 'stage', 'supplier', 'cost_per_unit', 'notes']
    
    def create(self, validated_data):
        validated_data['current_quantity'] = validated_data['initial_quantity']
        validated_data['current_average_weight'] = validated_data['initial_average_weight']
        return super().create(validated_data)
