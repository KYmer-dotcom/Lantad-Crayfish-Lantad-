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

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError
        if self.location == 'Main Pond':
            if (self.capacity or 0) > 2000:
                raise ValidationError({'capacity': 'Main Pond capacity cannot exceed 2,000.'})

    def save(self, *args, **kwargs):
        if self.location == 'Main Pond' and (self.capacity or 0) > 2000:
            raise ValueError(f"Main Pond capacity cannot exceed 2,000 (attempted: {self.capacity}).")
        if self.location == 'Breeding Pond' and not self.pk:
            if not self.capacity_2 and (self.capacity or 0) > 0:
                self.capacity_2 = (self.capacity or 0) * 250
            if not self.product_name_2:
                self.product_name_2 = 'Crilings'
        super().save(*args, **kwargs)

    
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
    def superworm_count(self):
        if self.location == 'Superworm Cabin':
            return (self.capacity or 0) * 200
        return self.capacity or 0

    @property
    def crilings_count(self):
        if self.location == 'Breeding Pond':
            if self.capacity_2 is not None and self.capacity_2 > 0:
                return self.capacity_2
            if not self.pk:
                return (self.capacity or 0) * 250
            from django.db.models import Sum
            outgoing_total = self.outgoing_transfers.aggregate(Sum('quantity'))['quantity__sum'] or 0
            mortality_total = self.mortality_logs.filter(product_name__icontains='Criling').aggregate(Sum('quantity'))['quantity__sum'] or 0
            if outgoing_total > 0 or mortality_total > 0:
                return max(0, self.capacity_2 or 0)
            return (self.capacity or 0) * 250
        return self.capacity_2 or 0

    @property
    def breeder_feed_grams(self):
        return round((self.capacity or 0) * 2.0, 1)

    @property
    def crilings_feed_grams(self):
        return round((self.crilings_count or 0) * 0.02, 1)

    @property
    def sw_breeder_feed_grams(self):
        return round((self.capacity or 0) * 0.1, 1)

    @property
    def sw_yield_feed_grams(self):
        return round((self.superworm_count or 0) * 0.05, 1)

    @property
    def main_crayfish_feed_grams(self):
        return round((self.capacity or 0) * 2.5, 1)

    @property
    def current_azula_quantity(self):
        if self.location == 'Azula':
            if self.status == 'empty':
                return 0
            days = self.days_since_transfer or 0
            return max(0, (self.capacity or 0) + (days * 2))
        return self.capacity or 0


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
    def harvest_readiness_status(self):
        """
        Calculates harvest readiness stage:
        - 'empty': Inactive / empty pond
        - 'maintenance': In maintenance
        - 'ready': Reached or passed target harvest date
        - 'near': Approaching target harvest date (within pre-harvest threshold)
        - 'far': Early or mid growth stage, far from harvest
        """
        if self.status == 'empty':
            return 'empty'
        if self.status == 'maintenance':
            return 'maintenance'
        if (self.capacity or 0) <= 0 and (self.female_quantity or 0) <= 0 and (self.male_quantity or 0) <= 0:
            return 'empty'
        if not self.transfer_date or self.days_since_transfer is None:
            return 'far'

        target = self.harvest_due_target_days
        days = self.days_since_transfer

        if days >= target:
            return 'ready'

        # Pre-harvest near thresholds:
        # Main Pond (150d target): within 30 days (days >= 120)
        # Superworm Cabin (90d target): within 30 days (days >= 60)
        # Breeding Pond Crilings (60d target): within 15 days (days >= 45)
        # Breeding Pond Reproduction (21d target): within 7 days (days >= 14)
        # Azula (30d target): within 10 days (days >= 20)
        if self.location == 'Main Pond':
            near_threshold = 120
        elif self.location == 'Superworm Cabin':
            near_threshold = 60
        elif self.location == 'Breeding Pond':
            near_threshold = 45 if self.breeding_type == 'Crilings' else 14
        elif self.location == 'Azula':
            near_threshold = 20
        else:
            near_threshold = int(target * 0.75)

        if days >= near_threshold:
            return 'near'
        return 'far'

    @property
    def harvest_readiness_display(self):
        status = self.harvest_readiness_status
        mapping = {
            'ready': 'Ready',
            'near': 'Near',
            'far': 'Far',
            'empty': 'Empty',
            'maintenance': 'Maintenance',
        }
        return mapping.get(status, 'Far')

    def get_mortality_stats(self, days=7):
        """
        Calculates mortality count and rate for this pond over given days.
        For Breeding Pond, tracks Product 1 (Breeder Crayfish), excluding Crilings.
        """
        from django.utils import timezone
        from datetime import timedelta
        from django.db.models import Sum

        today = timezone.localdate()
        qs = self.mortality_logs.all()
        if days:
            qs = qs.filter(date__gte=today - timedelta(days=days))
        if self.location == 'Breeding Pond':
            qs = qs.exclude(product_name__icontains='Criling')

        dead = qs.aggregate(Sum('quantity'))['quantity__sum'] or 0
        stock = self.capacity or 0
        total = stock + dead
        rate = round((dead / total) * 100, 1) if total > 0 else 0.0
        return {'dead': dead, 'rate': rate, 'total': total}

    @property
    def mortality_rate_7d(self):
        return self.get_mortality_stats(days=7)['rate']

    @property
    def mortality_rate_30d(self):
        return self.get_mortality_stats(days=30)['rate']

    def deduct_stock(self, quantity, product_name=None):
        """
        Deducts quantity from this pond. If transfer batches exist (e.g. in Main Pond),
        always deducts in FIFO order from the oldest transferred batch first.
        If product is Crilings in a Breeding Pond, deducts from capacity_2.
        """
        if quantity <= 0:
            return 0

        if self.location == 'Breeding Pond' and product_name and 'criling' in str(product_name).lower():
            current = self.crilings_count
            to_deduct = min(current, quantity)
            self.capacity_2 = max(0, current - to_deduct)
            self.save(update_fields=['capacity_2', 'updated_at'])
            return to_deduct

        if self.location == 'Azula':
            from django.utils import timezone
            current = self.current_azula_quantity
            to_deduct = min(current, quantity)
            remaining = max(0, current - to_deduct)
            self.capacity = remaining
            self.transfer_date = timezone.localdate() if self.capacity > 0 else None
            if self.capacity <= 0:
                self.status = Pond.Status.EMPTY
            else:
                self.status = Pond.Status.ACTIVE
            self.save(update_fields=['capacity', 'status', 'transfer_date', 'updated_at'])
            return to_deduct

        actual_deducted = 0
        remaining = quantity

        if self.transfer_batches.exists():
            for batch in self.transfer_batches.order_by('transfer_date', 'created_at', 'id'):
                if remaining <= 0:
                    break
                if batch.quantity <= remaining:
                    remaining -= batch.quantity
                    actual_deducted += batch.quantity
                    batch.delete()
                else:
                    batch.quantity -= remaining
                    actual_deducted += remaining
                    batch.save(update_fields=['quantity'])
                    remaining = 0

            remaining_batch_total = sum(b.quantity for b in self.transfer_batches.all())
            self.capacity = remaining_batch_total
            if self.capacity <= 0:
                self.capacity = 0
                self.status = Pond.Status.EMPTY
                self.transfer_date = None
            else:
                self.status = Pond.Status.ACTIVE
                earliest = self.transfer_batches.order_by('transfer_date', 'created_at').first()
                if earliest and earliest.transfer_date:
                    self.transfer_date = earliest.transfer_date
            self.save(update_fields=['capacity', 'status', 'transfer_date', 'updated_at'])
        else:
            to_deduct = min(self.capacity or 0, quantity)
            self.capacity = max(0, (self.capacity or 0) - to_deduct)
            actual_deducted = to_deduct
            if self.capacity <= 0:
                self.capacity = 0
                if self.location != 'Breeding Pond' and self.product_name_2 and self.capacity_2:
                    self.product_name = self.product_name_2
                    self.capacity = self.capacity_2
                    self.product_name_2 = ''
                    self.capacity_2 = 0
                    self.status = Pond.Status.ACTIVE
                elif self.location == 'Breeding Pond':
                    # In Breeding Pond, Breeder depletion does NOT empty or erase Crilings!
                    if (self.capacity_2 or 0) <= 0:
                        self.status = Pond.Status.EMPTY
                        self.transfer_date = None
                    else:
                        self.status = Pond.Status.ACTIVE
                else:
                    self.status = Pond.Status.EMPTY
                    self.transfer_date = None
            else:
                self.status = Pond.Status.ACTIVE
            self.save(update_fields=['capacity', 'status', 'transfer_date', 'updated_at'])

        return actual_deducted


class PondFeedingLog(models.Model):
    """Logs feeding operations for a pond."""
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE, related_name='feeding_logs')
    product_name = models.CharField(max_length=100, blank=True, default='')
    feed_type = models.ForeignKey('feed.FeedType', on_delete=models.SET_NULL, null=True, blank=True)
    quantity_grams = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Amount fed in grams")
    fed = models.BooleanField(default=False)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pond Feeding Log'
        verbose_name_plural = 'Pond Feeding Logs'
        ordering = ['-recorded_at']

    def __str__(self):
        prod = f" ({self.product_name})" if self.product_name else ""
        return f"{self.pond.name}{prod} - Fed: {self.fed} at {self.recorded_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def quantity_kg(self):
        if self.quantity_grams is not None:
            return round(float(self.quantity_grams) / 1000.0, 3)
        return 0.0


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

    @property
    def feed_grams(self):
        return round((self.quantity or 0) * 2.5, 1)


class PondMortalityLog(models.Model):
    """Logs daily mortality for a pond and product."""
    pond = models.ForeignKey(Pond, on_delete=models.CASCADE, related_name='mortality_logs')
    product_name = models.CharField(max_length=100, default='Breeder Crayfish')
    quantity = models.IntegerField(default=0, help_text="Number of mortalities")
    reason = models.TextField(blank=True, default='', help_text="Reason / cause of death")
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pond Mortality Log'
        verbose_name_plural = 'Pond Mortality Logs'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.pond.name} - {self.quantity} {self.product_name} ({self.date}): {self.reason}"
