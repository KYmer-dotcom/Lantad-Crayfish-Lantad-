"""
HARVEST MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError

from apps.accounts.access import is_owner
from .models import HarvestSchedule, HarvestRecord
from .serializers import HarvestScheduleSerializer, HarvestRecordSerializer


class HarvestScheduleViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Harvest Schedules.
    """
    
    queryset = HarvestSchedule.objects.select_related('stock_batch', 'created_by').all()
    serializer_class = HarvestScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['scheduled_date', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        if is_owner(self.request.user):
            return HarvestSchedule.objects.select_related('stock_batch', 'created_by').all()


class HarvestRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Harvest Records.
    """
    
    queryset = HarvestRecord.objects.select_related('stock_batch', 'harvested_by', 'harvest_schedule').all()
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['harvest_date', 'total_weight_kg', 'created_at']
    
    def perform_create(self, serializer):
        stock_batch = serializer.validated_data['stock_batch']
        quantity_harvested = serializer.validated_data['quantity_harvested']
        if quantity_harvested > stock_batch.current_quantity:
            raise ValidationError(
                f'Cannot harvest {quantity_harvested} fish from {stock_batch.batch_code}. '
                f'Available: {stock_batch.current_quantity}.'
            )
        harvest = serializer.save(harvested_by=self.request.user)
        # Update fish batch quantity
        harvest.stock_batch.current_quantity -= harvest.quantity_harvested
        if harvest.stock_batch.current_quantity <= 0:
            harvest.stock_batch.current_quantity = 0
            harvest.stock_batch.is_active = False
            harvest.stock_batch.pond.status = 'empty'
            harvest.stock_batch.pond.save(update_fields=['status'])
        harvest.stock_batch.save(update_fields=['current_quantity', 'is_active', 'updated_at'])

    def get_queryset(self):
        if is_owner(self.request.user):
            return HarvestRecord.objects.select_related('stock_batch', 'harvested_by', 'harvest_schedule').all()
