"""
FEED MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import FeedType, FeedInventory, FeedingLog
from .serializers import FeedTypeSerializer, FeedInventorySerializer, FeedingLogSerializer


class FeedTypeViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Feed Types.
    """
    
    queryset = FeedType.objects.all()
    serializer_class = FeedTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'brand']
    ordering_fields = ['name', 'price_per_kg', 'created_at']


class FeedInventoryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Feed Inventory.
    """
    
    queryset = FeedInventory.objects.select_related('feed_type', 'added_by').all()
    serializer_class = FeedInventorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['purchase_date', 'quantity_kg', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(added_by=self.request.user)


class FeedingLogViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Feeding Logs.
    """
    
    queryset = FeedingLog.objects.select_related('fish_batch', 'feed_type', 'fed_by').all()
    serializer_class = FeedingLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['feeding_time', 'quantity_kg', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(fed_by=self.request.user)
