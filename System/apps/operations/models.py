"""
=============================================================================
PONDS MODULE - Pond and Farm Management
=============================================================================
Manages fish ponds/farms including location and capacity.
=============================================================================
"""

from django.db import models
from django.conf import settings


class Farm(models.Model):
    """Farm/Site that contains multiple ponds."""
    
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    total_area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total area in square meters")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='farms')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Farm'
        verbose_name_plural = 'Farms'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def total_ponds(self):
        return self.ponds.count()
    
    @property
    def active_ponds(self):
        return self.ponds.filter(status='active').count()


class Pond(models.Model):
    """Individual pond within a farm."""
    
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        MAINTENANCE = 'maintenance', 'Under Maintenance'
        EMPTY = 'empty', 'Empty'
        HARVESTING = 'harvesting', 'Harvesting'
    
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='ponds')
    species = models.ManyToManyField('stock.Species', blank=True, related_name='ponds')
    name = models.CharField(max_length=100)
    caretaker_name = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=255, blank=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in square meters")
    depth = models.DecimalField(max_digits=5, decimal_places=2, help_text="Depth in meters")
    capacity = models.IntegerField(help_text="Maximum fish capacity", default=0)
    
    # Dynamic form fields
    product_name = models.CharField(max_length=100, blank=True)
    product_name_2 = models.CharField(max_length=100, blank=True, help_text="Second product name for dual tracking (e.g. Crilings)")
    transfer_date = models.DateField(null=True, blank=True)
    last_sanitized_date = models.DateField(null=True, blank=True, help_text="Date when this pond or tank was last sanitized")
    breeding_type = models.CharField(max_length=50, blank=True, help_text="e.g. Reproduction, Crilings")
    male_quantity = models.IntegerField(null=True, blank=True, default=0)
    female_quantity = models.IntegerField(null=True, blank=True, default=0)
    capacity_2 = models.IntegerField(null=True, blank=True, default=0, help_text="Quantity for second product")
    shelf_position = models.CharField(max_length=50, blank=True, help_text="For Superworm Cabin, e.g. Left-1-1")

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.EMPTY)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Pond'
        verbose_name_plural = 'Ponds'
        ordering = ['farm', 'name']
    
    def __str__(self):
        return f"{self.farm.name} - {self.name}"
    
    @property
    def current_stock_count(self):
        from apps.stock.models import StockBatch
        return StockBatch.objects.filter(pond=self, is_active=True).aggregate(
            total=models.Sum('current_quantity')
        )['total'] or 0

    @property
    def days_since_transfer(self):
        from django.utils import timezone
        if self.transfer_date:
            delta = timezone.localdate() - self.transfer_date
            return max(0, delta.days)
        return None

    @property
    def est_harvest_date(self):
        from datetime import timedelta
        if self.transfer_date and self.location == 'Main Pond':
            start_date = self.transfer_date + timedelta(days=150)
            end_date = self.transfer_date + timedelta(days=180)
            return f"{start_date.strftime('%b. %d, %Y')} - {end_date.strftime('%b. %d, %Y')}"
        return None

    @property
    def est_sw_harvest_date(self):
        from datetime import timedelta
        if self.transfer_date and self.location == 'Superworm Cabin':
            start_date = self.transfer_date + timedelta(days=90)
            end_date = self.transfer_date + timedelta(days=120)
            return f"{start_date.strftime('%b. %d, %Y')} - {end_date.strftime('%b. %d, %Y')}"
        return None

    @property
    def est_azula_harvest_date(self):
        from datetime import timedelta
        if self.transfer_date and self.location == 'Azula':
            harvest_date = self.transfer_date + timedelta(days=30)
            return harvest_date.strftime('%b. %d, %Y')
        return None

    @property
    def next_sanitization_date(self):
        from datetime import timedelta
        base_date = self.last_sanitized_date or self.transfer_date
        if base_date:
            return base_date + timedelta(days=15)
        return None

    @property
    def sanitization_days_remaining(self):
        from django.utils import timezone
        today = timezone.localdate()
        target = self.next_sanitization_date
        if not target:
            return 0
        return (target - today).days

    @property
    def is_sanitization_due(self):
        if not self.next_sanitization_date:
            return True
        return self.sanitization_days_remaining <= 0

    @property
    def est_transfer_date(self):
        from datetime import timedelta
        if self.transfer_date and self.breeding_type == 'Reproduction':
            return self.transfer_date + timedelta(days=21)
        return None

    @property
    def est_pond_transfer_date(self):
        from datetime import timedelta
        if self.transfer_date and self.breeding_type == 'Crilings':
            return self.transfer_date + timedelta(days=60)
        return None

    @property
    def harvest_due_target_days(self):
        if self.location == 'Main Pond':
            return 150
        elif self.location == 'Superworm Cabin':
            return 90
        elif self.location == 'Azula':
            return 30
        elif self.location == 'Breeding Pond':
            if self.breeding_type == 'Reproduction':
                return 21
            elif self.breeding_type == 'Crilings':
                return 60
        return 150

    @property
    def is_harvest_due(self):
        if not self.transfer_date or self.status == 'empty':
            return False
        if self.capacity <= 0 and (self.female_quantity or 0) <= 0 and (self.male_quantity or 0) <= 0:
            return False
        days = self.days_since_transfer
        if days is None:
            return False
        return days >= self.harvest_due_target_days

    @property
    def days_until_harvest(self):
        if not self.transfer_date:
            return None
        target = self.harvest_due_target_days
        days = self.days_since_transfer or 0
        remaining = target - days
        return max(0, remaining)


class PondFeedingLog(models.Model):
    """Logs feeding operations for a pond."""
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE, related_name='feeding_logs')
    feed_type = models.ForeignKey('feed.FeedType', on_delete=models.SET_NULL, null=True, blank=True)
    fed = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pond Feeding Log'
        verbose_name_plural = 'Pond Feeding Logs'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.pond.name} - Fed: {self.fed} at {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"


class PondTransferBatch(models.Model):
    """Tracks individual transfer batches and dates into a pond (e.g. from Breeding Pond to Main Pond)."""
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE, related_name='transfer_batches')
    source_pond = models.ForeignKey(Pond, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_transfers')
    product_name = models.CharField(max_length=100, default='Crilings')
    quantity = models.IntegerField(default=0)
    transfer_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    transferred_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pond Transfer Batch'
        verbose_name_plural = 'Pond Transfer Batches'
        ordering = ['transfer_date', 'created_at']

    def __str__(self):
        return f"{self.pond.name} - {self.quantity} {self.product_name} on {self.transfer_date}"
