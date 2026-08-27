"""
=============================================================================
ANALYTICS MODULE - Data Analytics and Forecasting
=============================================================================
Stores forecast data and analytical reports for decision making.
=============================================================================
"""

from django.db import models
from django.conf import settings


class HarvestForecast(models.Model):
    """Harvest date and yield predictions."""
    
    stock_batch = models.ForeignKey('stock.StockBatch', on_delete=models.CASCADE, related_name='harvest_forecasts')
    forecast_date = models.DateField(help_text="Date when forecast was made")
    predicted_harvest_date = models.DateField()
    predicted_weight = models.DecimalField(max_digits=8, decimal_places=2, help_text="Predicted average weight in grams")
    predicted_quantity = models.IntegerField()
    predicted_total_yield = models.DecimalField(max_digits=12, decimal_places=2, help_text="Predicted total yield in kg")
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2, help_text="Confidence percentage")
    algorithm_used = models.CharField(max_length=50, default='linear_regression')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Harvest Forecast'
        verbose_name_plural = 'Harvest Forecasts'
        ordering = ['-forecast_date']
    
    def __str__(self):
        return f"{self.stock_batch.batch_code} - Forecast for {self.predicted_harvest_date}"


class SalesForecast(models.Model):
    """Sales demand predictions."""
    
    forecast_date = models.DateField(help_text="Date when forecast was made")
    period_start = models.DateField()
    period_end = models.DateField()
    predicted_demand_kg = models.DecimalField(max_digits=12, decimal_places=2)
    predicted_revenue = models.DecimalField(max_digits=14, decimal_places=2)
    species = models.ForeignKey('stock.Species', on_delete=models.CASCADE, null=True, blank=True)
    confidence_level = models.DecimalField(max_digits=5, decimal_places=2)
    algorithm_used = models.CharField(max_length=50, default='moving_average')
    actual_demand_kg = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    actual_revenue = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sales Forecast'
        verbose_name_plural = 'Sales Forecasts'
        ordering = ['-forecast_date']
    
    def __str__(self):
        return f"Sales Forecast: {self.period_start} to {self.period_end}"
    
    @property
    def accuracy(self):
        if self.actual_demand_kg and self.predicted_demand_kg:
            error = abs(self.actual_demand_kg - self.predicted_demand_kg)
            return max(0, (1 - (error / self.predicted_demand_kg)) * 100)
        return None

