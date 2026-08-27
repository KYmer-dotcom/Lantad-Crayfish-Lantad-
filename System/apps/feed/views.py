"""
FEED MODULE - Views
"""

from decimal import Decimal
from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.accounts.access import is_owner
from .models import FeedType, FeedInventory, FeedingLog, FeedStockMovement
from .services import record_stock_in, consume_feed
from .serializers import (
    FeedTypeSerializer,
    FeedInventorySerializer,
    FeedingLogSerializer,
    FeedStockMovementSerializer,
)


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
        inventory = serializer.save(added_by=self.request.user)
        record_stock_in(inventory, self.request.user)


class FeedingLogViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Feeding Logs.
    """
    
    queryset = FeedingLog.objects.select_related('stock_batch', 'feed_type', 'fed_by').all()
    serializer_class = FeedingLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['feeding_time', 'quantity_kg', 'created_at']
    
    def perform_create(self, serializer):
        with transaction.atomic():
            feeding_log = serializer.save(fed_by=self.request.user)
            try:
                consume_feed(
                    feed_type=feeding_log.feed_type,
                    quantity_kg=feeding_log.quantity_kg,
                    user=self.request.user,
                    feeding_log=feeding_log,
                )
            except DjangoValidationError as exc:
                raise ValidationError(exc.message)

    def get_queryset(self):
        if is_owner(self.request.user):
            return FeedingLog.objects.select_related('stock_batch', 'feed_type', 'fed_by').all()


class FeedStockMovementViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Feed Stock Movements.
    """

    queryset = FeedStockMovement.objects.select_related('feed_type', 'moved_by').all()
    serializer_class = FeedStockMovementSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['moved_at', 'delta_kg']

    def perform_create(self, serializer):
        movement = serializer.save(moved_by=self.request.user)
        if movement.movement_type == FeedStockMovement.MovementType.OUT and movement.delta_kg > 0:
            movement.delta_kg = Decimal('0.00') - movement.delta_kg
            movement.save(update_fields=['delta_kg'])
        if movement.movement_type == FeedStockMovement.MovementType.IN and movement.delta_kg < 0:
            movement.delta_kg = abs(movement.delta_kg)
            movement.save(update_fields=['delta_kg'])

    def get_queryset(self):
        if is_owner(self.request.user):
            return FeedStockMovement.objects.select_related('feed_type', 'moved_by').all()
