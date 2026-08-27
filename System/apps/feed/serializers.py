"""
FEED MODULE - Serializers
"""

from rest_framework import serializers
from .models import FeedType, FeedInventory, FeedingLog, FeedStockMovement


class FeedTypeSerializer(serializers.ModelSerializer):
    """Serializer for FeedType model."""
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    current_stock_kg = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedType
        fields = ['id', 'name', 'brand', 'category', 'category_display',
                  'protein_content', 'price_per_kg', 'current_stock_kg', 'description', 'is_active',
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
    
    stock_batch_code = serializers.CharField(source='stock_batch.batch_code', read_only=True)
    feed_type_name = serializers.CharField(source='feed_type.name', read_only=True)
    fed_by_name = serializers.CharField(source='fed_by.username', read_only=True)
    feed_cost = serializers.ReadOnlyField()
    
    class Meta:
        model = FeedingLog
        fields = ['id', 'stock_batch', 'stock_batch_code', 'feed_type', 'feed_type_name',
                  'quantity_kg', 'feeding_time', 'fed_by', 'fed_by_name',
                  'feed_cost', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class FeedStockMovementSerializer(serializers.ModelSerializer):
    """Serializer for FeedStockMovement model."""

    feed_type_name = serializers.CharField(source='feed_type.name', read_only=True)
    moved_by_name = serializers.CharField(source='moved_by.username', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)

    class Meta:
        model = FeedStockMovement
        fields = [
            'id', 'feed_type', 'feed_type_name', 'movement_type', 'movement_type_display',
            'delta_kg', 'moved_at', 'moved_by', 'moved_by_name', 'notes',
            'feed_inventory', 'feeding_log'
        ]
        read_only_fields = ['id', 'moved_at']
