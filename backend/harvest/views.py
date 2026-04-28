"""
HARVEST MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter

from .models import HarvestSchedule, HarvestRecord
from .serializers import HarvestScheduleSerializer, HarvestRecordSerializer


class HarvestScheduleViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Harvest Schedules.
    """
    
    queryset = HarvestSchedule.objects.select_related('fish_batch', 'created_by').all()
    serializer_class = HarvestScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['scheduled_date', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class HarvestRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Harvest Records.
    """
    
    queryset = HarvestRecord.objects.select_related('fish_batch', 'harvested_by', 'harvest_schedule').all()
    serializer_class = HarvestRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['harvest_date', 'total_weight_kg', 'created_at']
    
    def perform_create(self, serializer):
        harvest = serializer.save(harvested_by=self.request.user)
        # Update fish batch quantity
        harvest.fish_batch.current_quantity -= harvest.quantity_harvested
        if harvest.fish_batch.current_quantity <= 0:
            harvest.fish_batch.is_active = False
            harvest.fish_batch.pond.status = 'empty'
            harvest.fish_batch.pond.save()
        harvest.fish_batch.save()
