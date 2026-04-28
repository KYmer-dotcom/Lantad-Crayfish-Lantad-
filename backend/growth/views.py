"""
GROWTH MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter

from .models import GrowthSample, MortalityRecord
from .serializers import GrowthSampleSerializer, MortalityRecordSerializer


class GrowthSampleViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Growth Samples.
    """
    
    queryset = GrowthSample.objects.select_related('fish_batch', 'sampled_by').all()
    serializer_class = GrowthSampleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['sample_date', 'average_weight', 'created_at']
    
    def perform_create(self, serializer):
        sample = serializer.save(sampled_by=self.request.user)
        # Update fish batch current average weight
        sample.fish_batch.current_average_weight = sample.average_weight
        sample.fish_batch.save()


class MortalityRecordViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Mortality Records.
    """
    
    queryset = MortalityRecord.objects.select_related('fish_batch', 'recorded_by').all()
    serializer_class = MortalityRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['record_date', 'quantity', 'created_at']
    
    def perform_create(self, serializer):
        mortality = serializer.save(recorded_by=self.request.user)
        # Update fish batch current quantity
        mortality.fish_batch.current_quantity -= mortality.quantity
        mortality.fish_batch.save()
