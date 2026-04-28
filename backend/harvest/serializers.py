"""
HARVEST MODULE - Serializers
"""

from rest_framework import serializers
from .models import HarvestSchedule, HarvestRecord


class HarvestScheduleSerializer(serializers.ModelSerializer):
    """Serializer for HarvestSchedule model."""
    
    fish_batch_code = serializers.CharField(source='fish_batch.batch_code', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = HarvestSchedule
        fields = ['id', 'fish_batch', 'fish_batch_code', 'scheduled_date',
                  'estimated_quantity', 'estimated_total_weight', 'target_weight',
                  'status', 'status_display', 'notes', 'created_by', 'created_by_name',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class HarvestRecordSerializer(serializers.ModelSerializer):
    """Serializer for HarvestRecord model."""
    
    fish_batch_code = serializers.CharField(source='fish_batch.batch_code', read_only=True)
    harvested_by_name = serializers.CharField(source='harvested_by.username', read_only=True)
    
    class Meta:
        model = HarvestRecord
        fields = ['id', 'harvest_schedule', 'fish_batch', 'fish_batch_code',
                  'harvest_date', 'quantity_harvested', 'total_weight_kg',
                  'average_weight_per_fish', 'grade_a_quantity', 'grade_b_quantity',
                  'grade_c_quantity', 'is_partial_harvest', 'harvested_by',
                  'harvested_by_name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
