from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter

from .models import HarvestForecast, SalesForecast
from .serializers import HarvestForecastSerializer, SalesForecastSerializer


class HarvestForecastViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Harvest Forecasts.
    """
    
    queryset = HarvestForecast.objects.select_related('stock_batch').all()
    serializer_class = HarvestForecastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['forecast_date', 'predicted_harvest_date', 'created_at']


class SalesForecastViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Sales Forecasts.
    """
    
    queryset = SalesForecast.objects.select_related('species').all()
    serializer_class = SalesForecastSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['forecast_date', 'period_start', 'created_at']

