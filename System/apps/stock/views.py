"""
FISH MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.access import filter_by_pond, is_owner
from .models import Species, StockBatch
from .serializers import SpeciesSerializer, StockBatchSerializer, StockBatchCreateSerializer


class SpeciesViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Fish Species.
    """
    
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'scientific_name']
    ordering_fields = ['name', 'created_at']


class StockBatchViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Stock Batches.
    """
    
    queryset = StockBatch.objects.select_related('pond', 'species', 'stocked_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['batch_code', 'species__name', 'pond__name']
    ordering_fields = ['stocking_date', 'current_quantity', 'created_at']

    def get_queryset(self):
        if is_owner(self.request.user):
            return StockBatch.objects.select_related('pond', 'species', 'stocked_by').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return StockBatchCreateSerializer
        return StockBatchSerializer
    
    def perform_create(self, serializer):
        serializer.save(stocked_by=self.request.user)
