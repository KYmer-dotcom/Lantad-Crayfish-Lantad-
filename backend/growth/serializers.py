"""
GROWTH MODULE - Serializers
"""

from rest_framework import serializers
from .models import GrowthSample, MortalityRecord


class GrowthSampleSerializer(serializers.ModelSerializer):
    """Serializer for GrowthSample model."""
    
    fish_batch_code = serializers.CharField(source='fish_batch.batch_code', read_only=True)
    sampled_by_name = serializers.CharField(source='sampled_by.username', read_only=True)
    weight_gain = serializers.ReadOnlyField()
    
    class Meta:
        model = GrowthSample
        fields = ['id', 'fish_batch', 'fish_batch_code', 'sample_date', 'sample_size',
                  'average_weight', 'min_weight', 'max_weight', 'average_length',
                  'sampled_by', 'sampled_by_name', 'weight_gain', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class MortalityRecordSerializer(serializers.ModelSerializer):
    """Serializer for MortalityRecord model."""
    
    fish_batch_code = serializers.CharField(source='fish_batch.batch_code', read_only=True)
    recorded_by_name = serializers.CharField(source='recorded_by.username', read_only=True)
    cause_display = serializers.CharField(source='get_cause_display', read_only=True)
    
    class Meta:
        model = MortalityRecord
        fields = ['id', 'fish_batch', 'fish_batch_code', 'record_date', 'quantity',
                  'cause', 'cause_display', 'estimated_weight_loss',
                  'recorded_by', 'recorded_by_name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
