"""
=============================================================================
GROWTH MODULE - Growth and Mortality Monitoring
=============================================================================
Tracks fish growth sampling data and mortality records.
=============================================================================
"""

from django.db import models
from django.conf import settings


class GrowthSample(models.Model):
    """Growth sampling records for fish batches."""
    
    fish_batch = models.ForeignKey('fish.FishBatch', on_delete=models.CASCADE, related_name='growth_samples')
    sample_date = models.DateField()
    sample_size = models.IntegerField(help_text="Number of fish sampled")
    average_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Average weight in grams")
    min_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    max_weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    average_length = models.DecimalField(max_digits=6, decimal_places=2, help_text="Average length in cm", null=True, blank=True)
    sampled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Growth Sample'
        verbose_name_plural = 'Growth Samples'
        ordering = ['-sample_date']
    
    def __str__(self):
        return f"{self.fish_batch.batch_code} - {self.sample_date}"
    
    @property
    def weight_gain(self):
        """Calculate weight gain from initial weight."""
        return self.average_weight - self.fish_batch.initial_average_weight


class MortalityRecord(models.Model):
    """Mortality records for fish batches."""
    
    class Cause(models.TextChoices):
        DISEASE = 'disease', 'Disease'
        WATER_QUALITY = 'water_quality', 'Poor Water Quality'
        PREDATION = 'predation', 'Predation'
        HANDLING = 'handling', 'Handling Stress'
        UNKNOWN = 'unknown', 'Unknown'
        OTHER = 'other', 'Other'
    
    fish_batch = models.ForeignKey('fish.FishBatch', on_delete=models.CASCADE, related_name='mortality_records')
    record_date = models.DateField()
    quantity = models.IntegerField(help_text="Number of fish died")
    cause = models.CharField(max_length=20, choices=Cause.choices, default=Cause.UNKNOWN)
    estimated_weight_loss = models.DecimalField(
        max_digits=10, decimal_places=2,
        help_text="Total weight lost in grams",
        null=True, blank=True
    )
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Mortality Record'
        verbose_name_plural = 'Mortality Records'
        ordering = ['-record_date']
    
    def __str__(self):
        return f"{self.fish_batch.batch_code} - {self.quantity} died on {self.record_date}"
