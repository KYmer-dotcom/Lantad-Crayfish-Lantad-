"""
PONDS MODULE - Serializers
"""

from rest_framework import serializers
from .models import Farm, Pond


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
    manager_name = serializers.CharField(source='manager.username', read_only=True)
    species_names = serializers.SerializerMethodField()
    current_stock_count = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    def get_species_names(self, obj):
        return [species.name for species in obj.species.all()]
    
    class Meta:
        model = Pond
        fields = ['id', 'farm', 'farm_name', 'manager', 'manager_name', 'name',
                  'caretaker_name', 'location', 'size', 'depth', 'capacity', 'species', 'species_names',
                  'status', 'status_display', 'current_stock_count', 'description',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
