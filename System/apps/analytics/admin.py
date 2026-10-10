from django.contrib import admin
from .models import HarvestForecast, SalesForecast


@admin.register(HarvestForecast)
class HarvestForecastAdmin(admin.ModelAdmin):
    list_display = ('stock_batch', 'predicted_harvest_date', 'predicted_weight', 'predicted_total_yield', 'confidence_level', 'algorithm_used')


@admin.register(SalesForecast)
class SalesForecastAdmin(admin.ModelAdmin):
    list_display = ('forecast_date', 'period_start', 'period_end', 'predicted_demand_kg', 'predicted_revenue', 'confidence_level', 'algorithm_used')
