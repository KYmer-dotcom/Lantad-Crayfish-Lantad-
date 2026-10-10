from django.contrib import admin
from .models import HarvestSchedule, HarvestRecord


@admin.register(HarvestSchedule)
class HarvestScheduleAdmin(admin.ModelAdmin):
    list_display = ('stock_batch', 'scheduled_date', 'estimated_quantity', 'estimated_total_weight', 'status')
    list_filter = ('status', 'scheduled_date')
    search_fields = ('stock_batch__batch_code',)


@admin.register(HarvestRecord)
class HarvestRecordAdmin(admin.ModelAdmin):
    list_display = ('stock_batch', 'harvest_date', 'quantity_harvested', 'total_weight_kg', 'average_weight_per_fish', 'harvested_by')
    list_filter = ('harvest_date', 'is_partial_harvest')
    search_fields = ('stock_batch__batch_code',)
