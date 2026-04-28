"""
=============================================================================
FISH MODULE - Fish Stocking and Classification Management
=============================================================================
Manages fish species, classifications, and batch stocking records.
=============================================================================
"""

from django.db import models
from django.conf import settings


class Species(models.Model):
    """Fish species classification."""
    
    name = models.CharField(max_length=100, unique=True)
    scientific_name = models.CharField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    average_growth_rate = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="Average growth rate in grams per day",
        null=True, blank=True
    )
    optimal_temperature_min = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    optimal_temperature_max = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    optimal_ph_min = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    optimal_ph_max = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Species'
        verbose_name_plural = 'Species'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class FishBatch(models.Model):
    """Batch of fish stocked in a pond."""
    
    class Stage(models.TextChoices):
        FRY = 'fry', 'Fry'
        FINGERLING = 'fingerling', 'Fingerling'
        JUVENILE = 'juvenile', 'Juvenile'
        ADULT = 'adult', 'Adult'
        MARKET_SIZE = 'market_size', 'Market Size'
    
    pond = models.ForeignKey('ponds.Pond', on_delete=models.CASCADE, related_name='fish_batches')
    species = models.ForeignKey(Species, on_delete=models.PROTECT, related_name='batches')
    batch_code = models.CharField(max_length=50, unique=True)
    stocking_date = models.DateField()
    initial_quantity = models.IntegerField()
    current_quantity = models.IntegerField()
    initial_average_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Initial weight in grams")
    current_average_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Current weight in grams")
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.FRY)
    supplier = models.CharField(max_length=200, blank=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    stocked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Fish Batch'
        verbose_name_plural = 'Fish Batches'
        ordering = ['-stocking_date']
    
    def __str__(self):
        return f"{self.batch_code} - {self.species.name}"
    
    @property
    def mortality_count(self):
        return self.initial_quantity - self.current_quantity
    
    @property
    def mortality_rate(self):
        if self.initial_quantity > 0:
            return (self.mortality_count / self.initial_quantity) * 100
        return 0
    
    @property
    def total_biomass(self):
        return self.current_quantity * self.current_average_weight
