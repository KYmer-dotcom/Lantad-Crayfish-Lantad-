"""
PONDS MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Farm, Pond, WaterQualityLog
from .serializers import FarmSerializer, PondSerializer, WaterQualityLogSerializer


class FarmViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Farms.
    """
    
    queryset = Farm.objects.all()
    serializer_class = FarmSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'created_at', 'total_area']
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PondViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Ponds.
    """
    
    queryset = Pond.objects.select_related('farm').all()
    serializer_class = PondSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'farm__name']
    ordering_fields = ['name', 'created_at', 'size', 'capacity']


class WaterQualityLogViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Water Quality Logs.
    """
    
    queryset = WaterQualityLog.objects.select_related('pond', 'recorded_by').all()
    serializer_class = WaterQualityLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['recorded_at', 'temperature', 'ph_level']
    
    def perform_create(self, serializer):
        serializer.save(recorded_by=self.request.user)
