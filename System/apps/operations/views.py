"""
PONDS MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.access import is_owner
from .models import Farm, Pond
from .serializers import FarmSerializer, PondSerializer


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

    def get_queryset(self):
        if is_owner(self.request.user):
            return Farm.objects.all()


class PondViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Ponds.
    """
    
    queryset = Pond.objects.select_related('farm').prefetch_related('species').all()
    serializer_class = PondSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'farm__name']
    ordering_fields = ['name', 'created_at', 'size', 'capacity']

    def get_queryset(self):
        if is_owner(self.request.user):
            return Pond.objects.select_related('farm', 'manager').prefetch_related('species').all()
