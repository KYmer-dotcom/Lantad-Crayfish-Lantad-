"""
FISH MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Species, FishBatch
from .serializers import SpeciesSerializer, FishBatchSerializer, FishBatchCreateSerializer


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


class FishBatchViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Fish Batches.
    """
    
    queryset = FishBatch.objects.select_related('pond', 'species', 'stocked_by').all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['batch_code', 'species__name', 'pond__name']
    ordering_fields = ['stocking_date', 'current_quantity', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return FishBatchCreateSerializer
        return FishBatchSerializer
    
    def perform_create(self, serializer):
        serializer.save(stocked_by=self.request.user)
