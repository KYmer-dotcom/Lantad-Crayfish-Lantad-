"""
PONDS MODULE - Serializers
"""

from rest_framework import serializers
from .models import Farm, Pond, WaterQualityLog


class FarmSerializer(serializers.ModelSerializer):
    """Serializer for Farm model."""
    
    total_ponds = serializers.ReadOnlyField()
    active_ponds = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Farm
        fields = ['id', 'name', 'location', 'total_area', 'owner', 'owner_name',
                  'description', 'is_active', 'total_ponds', 'active_ponds',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PondSerializer(serializers.ModelSerializer):
    """Serializer for Pond model."""
    
    farm_name = serializers.CharField(source='farm.name', read_only=True)
    current_stock_count = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Pond
        fields = ['id', 'farm', 'farm_name', 'name', 'size', 'depth', 'capacity',
                  'status', 'status_display', 'current_stock_count', 'description',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class WaterQualityLogSerializer(serializers.ModelSerializer):
    """Serializer for WaterQualityLog model."""
    
    pond_name = serializers.CharField(source='pond.name', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    
    class Meta:
        model = WaterQualityLog
        fields = ['id', 'pond', 'pond_name', 'recorded_by', 'recorded_by_name',
                  'temperature', 'ph_level', 'dissolved_oxygen', 'ammonia_level',
                  'notes', 'recorded_at']
        read_only_fields = ['id', 'recorded_at']
