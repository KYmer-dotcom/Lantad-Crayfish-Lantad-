from django.contrib import admin
from .models import Farm, Pond, PondFeedingLog, PondMortalityLog


@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'total_area', 'is_active')


@admin.register(Pond)
class PondAdmin(admin.ModelAdmin):
    list_display = ('name', 'farm', 'status', 'capacity', 'size')
    list_filter = ('status', 'farm')


@admin.register(PondFeedingLog)
class PondFeedingLogAdmin(admin.ModelAdmin):
    list_display = ('pond', 'feed_type', 'fed', 'recorded_by', 'recorded_at')
    list_filter = ('fed', 'recorded_at')


@admin.register(PondMortalityLog)
class PondMortalityLogAdmin(admin.ModelAdmin):
    list_display = ('pond', 'product_name', 'quantity', 'reason', 'date', 'recorded_by')
    list_filter = ('date', 'product_name')
