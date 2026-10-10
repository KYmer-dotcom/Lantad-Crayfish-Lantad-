from django.contrib import admin
from .models import Species, StockBatch, SpeciesStock


@admin.register(Species)
class SpeciesAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'scientific_name', 'market_weight_g', 'optimal_temperature_min', 'optimal_temperature_max')
    search_fields = ('name', 'scientific_name')
    list_filter = ('category',)


@admin.register(StockBatch)
class StockBatchAdmin(admin.ModelAdmin):
    list_display = ('batch_code', 'species', 'pond', 'stage', 'current_quantity', 'current_average_weight', 'is_active', 'stocking_date')
    search_fields = ('batch_code', 'species__name', 'pond__name')
    list_filter = ('stage', 'is_active', 'species')


@admin.register(SpeciesStock)
class SpeciesStockAdmin(admin.ModelAdmin):
    list_display = ('species', 'available_quantity', 'updated_at')
    search_fields = ('species__name',)
