"""
FEED MODULE - Serializers
"""

from rest_framework import serializers
from .models import FeedType, FeedInventory, FeedingLog


class FeedTypeSerializer(serializers.ModelSerializer):
    """Serializer for FeedType model."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = FeedType
        fields = ['id', 'name', 'brand', 'category', 'category_display',
                  'protein_content', 'price_per_kg', 'description', 'is_active',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FeedInventorySerializer(serializers.ModelSerializer):
    """Serializer for FeedInventory model."""
    
    feed_type_name = serializers.CharField(source='feed_type.name', read_only=True)
    added_by_name = serializers.CharField(source='added_by.username', read_only=True)
    
    class Meta:
        model = FeedInventory
        fields = ['id', 'feed_type', 'feed_type_name', 'quantity_kg', 'purchase_date',
                  'expiry_date', 'supplier', 'batch_number', 'total_cost',
                  'added_by', 'added_by_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeedingLogSerializer(serializers.ModelSerializer):
    """Serializer for FeedingLog model."""
    
    fish_batch_code = serializers.CharField(source='fish_batch.batch_code', read_only=True)
    feed_type_name = serializers.CharField(source='feed_type.name', read_only=True)
    fed_by_name = serializers.CharField(source='fed_by.username', read_only=True)
    feed_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedingLog
        fields = ['id', 'fish_batch', 'fish_batch_code', 'feed_type', 'feed_type_name',
                  'quantity_kg', 'feeding_time', 'fed_by', 'fed_by_name',
                  'feed_cost', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
