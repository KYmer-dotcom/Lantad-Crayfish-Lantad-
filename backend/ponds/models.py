"""
=============================================================================
PONDS MODULE - Pond and Farm Management
=============================================================================
Manages fish ponds/farms including location, capacity, and water quality.
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
    name = models.CharField(max_length=100)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in square meters")
    depth = models.DecimalField(max_digits=5, decimal_places=2, help_text="Depth in meters")
    capacity = models.IntegerField(help_text="Maximum fish capacity")
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
        from fish.models import FishBatch
        return FishBatch.objects.filter(pond=self, is_active=True).aggregate(
            total=models.Sum('current_quantity')
        )['total'] or 0


class WaterQualityLog(models.Model):
    """Water quality monitoring records for ponds."""
    
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE, related_name='water_quality_logs')
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, help_text="Temperature in Celsius")
    ph_level = models.DecimalField(max_digits=4, decimal_places=2)
    dissolved_oxygen = models.DecimalField(max_digits=5, decimal_places=2, help_text="DO in mg/L")
    ammonia_level = models.DecimalField(max_digits=5, decimal_places=3, help_text="Ammonia in mg/L", null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Water Quality Log'
        verbose_name_plural = 'Water Quality Logs'
        ordering = ['-recorded_at']
    
    def __str__(self):
        return f"{self.pond} - {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"
