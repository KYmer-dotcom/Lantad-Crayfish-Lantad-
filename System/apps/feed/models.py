"""
=============================================================================
FEED MODULE - Feed Consumption Tracking
=============================================================================
Tracks feed types, inventory, and daily feeding records.
=============================================================================
"""

from django.db import models
from django.conf import settings
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce


class FeedType(models.Model):
    """Types of fish feed available."""
    
    class Category(models.TextChoices):
        STARTER = 'starter', 'Starter Feed'
        GROWER = 'grower', 'Grower Feed'
        FINISHER = 'finisher', 'Finisher Feed'
        SPECIALTY = 'specialty', 'Specialty Feed'
    
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    accent_color = models.CharField(max_length=20, default='cyan')
    icon = models.CharField(max_length=20, default='box')
    protein_content = models.DecimalField(max_digits=5, decimal_places=2, help_text="Protein percentage")
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Feed Type'
        verbose_name_plural = 'Feed Types'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    @property
    def current_stock_kg(self):
        return FeedStockMovement.available_stock(self)


class FeedInventory(models.Model):
    """Feed inventory/stock management."""
    
    feed_type = models.ForeignKey(FeedType, on_delete=models.CASCADE, related_name='inventory')
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    supplier = models.CharField(max_length=200, blank=True)
    batch_number = models.CharField(max_length=50, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Feed Inventory'
        verbose_name_plural = 'Feed Inventories'
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.feed_type.name} - {self.quantity_kg}kg"


class FeedingLog(models.Model):
    """Daily feeding records for fish batches."""
    
    stock_batch = models.ForeignKey('stock.StockBatch', on_delete=models.CASCADE, related_name='feeding_logs')
    feed_type = models.ForeignKey(FeedType, on_delete=models.PROTECT, related_name='feeding_logs')
    quantity_kg = models.DecimalField(max_digits=8, decimal_places=2, help_text="Amount fed in kg")
    feeding_time = models.DateTimeField()
    fed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Feeding Log'
        verbose_name_plural = 'Feeding Logs'
        ordering = ['-feeding_time']
    
    def __str__(self):
        return f"{self.stock_batch.batch_code} - {self.feeding_time.strftime('%Y-%m-%d')}"
    
    @property
    def feed_cost(self):
        return self.quantity_kg * self.feed_type.price_per_kg


class FeedStockMovement(models.Model):
    """Stock movement ledger for feed supplies."""

    class MovementType(models.TextChoices):
        IN = 'in', 'Stock In'
        OUT = 'out', 'Stock Out'
        ADJUSTMENT = 'adjustment', 'Adjustment'

    feed_type = models.ForeignKey(FeedType, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    delta_kg = models.DecimalField(max_digits=10, decimal_places=2, help_text="Signed stock change in kg")
    moved_at = models.DateTimeField(auto_now_add=True)
    moved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    feed_inventory = models.ForeignKey(
        FeedInventory, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements'
    )
    feeding_log = models.ForeignKey(
        FeedingLog, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movements'
    )

    class Meta:
        verbose_name = 'Feed Stock Movement'
        verbose_name_plural = 'Feed Stock Movements'
        ordering = ['-moved_at']

    def __str__(self):
        return f"{self.feed_type.name} {self.delta_kg}kg ({self.get_movement_type_display()})"

    @classmethod
    def available_stock(cls, feed_type):
        return cls.objects.filter(feed_type=feed_type).aggregate(
            total=Coalesce(
                Sum('delta_kg'),
                Value(0),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )['total']
