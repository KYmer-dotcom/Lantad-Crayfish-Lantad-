from django.contrib import admin
from .models import FeedType, FeedInventory, FeedStockMovement, FeedingLog, FeedSack


@admin.register(FeedType)
class FeedTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price_per_kg', 'protein_content', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'brand')


@admin.register(FeedSack)
class FeedSackAdmin(admin.ModelAdmin):
    list_display = ('sack_code', 'feed_type', 'sack_number', 'current_weight_kg', 'initial_weight_kg', 'status', 'created_at')
    list_filter = ('feed_type',)
    search_fields = ('feed_type__name',)


@admin.register(FeedInventory)
class FeedInventoryAdmin(admin.ModelAdmin):
    list_display = ('feed_type', 'quantity_kg', 'total_cost', 'supplier', 'purchase_date', 'expiry_date')
    search_fields = ('feed_type__name', 'supplier', 'batch_number')


@admin.register(FeedingLog)
class FeedingLogAdmin(admin.ModelAdmin):
    list_display = ('stock_batch', 'feed_type', 'quantity_kg', 'feeding_time', 'fed_by')
    list_filter = ('feed_type', 'feeding_time')
    search_fields = ('stock_batch__batch_code',)


@admin.register(FeedStockMovement)
class FeedStockMovementAdmin(admin.ModelAdmin):
    list_display = ('feed_type', 'movement_type', 'delta_kg', 'moved_at', 'moved_by')
    list_filter = ('movement_type', 'moved_at')

