"""
=============================================================================
HARVEST MODULE - Harvest Management
=============================================================================
Manages harvest scheduling, records, and yield tracking.
=============================================================================
"""

from django.db import models
from django.conf import settings


class HarvestSchedule(models.Model):
    """Planned harvest schedules for fish batches."""
    
    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        POSTPONED = 'postponed', 'Postponed'
    
    fish_batch = models.ForeignKey('fish.FishBatch', on_delete=models.CASCADE, related_name='harvest_schedules')
    scheduled_date = models.DateField()
    estimated_quantity = models.IntegerField(help_text="Estimated number of fish to harvest")
    estimated_total_weight = models.DecimalField(max_digits=12, decimal_places=2, help_text="Estimated total weight in kg")
    target_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Target weight per fish in grams")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Harvest Schedule'
        verbose_name_plural = 'Harvest Schedules'
        ordering = ['scheduled_date']
    
    def __str__(self):
        return f"{self.fish_batch.batch_code} - {self.scheduled_date}"


class HarvestRecord(models.Model):
    """Actual harvest records."""
    
    harvest_schedule = models.ForeignKey(
        HarvestSchedule, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='harvest_records'
    )
    fish_batch = models.ForeignKey('fish.FishBatch', on_delete=models.CASCADE, related_name='harvest_records')
    harvest_date = models.DateField()
    quantity_harvested = models.IntegerField()
    total_weight_kg = models.DecimalField(max_digits=12, decimal_places=2, help_text="Total weight in kg")
    average_weight_per_fish = models.DecimalField(max_digits=8, decimal_places=2, help_text="Average weight in grams")
    grade_a_quantity = models.IntegerField(default=0, help_text="Premium grade fish count")
    grade_b_quantity = models.IntegerField(default=0, help_text="Standard grade fish count")
    grade_c_quantity = models.IntegerField(default=0, help_text="Below standard grade fish count")
    is_partial_harvest = models.BooleanField(default=False)
    harvested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Harvest Record'
        verbose_name_plural = 'Harvest Records'
        ordering = ['-harvest_date']
    
    def __str__(self):
        return f"{self.fish_batch.batch_code} - {self.harvest_date}"
