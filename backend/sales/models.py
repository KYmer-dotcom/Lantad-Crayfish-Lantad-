"""
=============================================================================
SALES MODULE - Sales and Product Distribution Monitoring
=============================================================================
Manages customers, sales orders, and delivery tracking.
=============================================================================
"""

from django.db import models
from django.conf import settings


class Customer(models.Model):
    """Customer/Buyer information."""
    
    class Type(models.TextChoices):
        INDIVIDUAL = 'individual', 'Individual'
        RETAILER = 'retailer', 'Retailer'
        WHOLESALER = 'wholesaler', 'Wholesaler'
        RESTAURANT = 'restaurant', 'Restaurant'
        EXPORTER = 'exporter', 'Exporter'
    
    name = models.CharField(max_length=200)
    customer_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INDIVIDUAL)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_customer_type_display()})"
    
    @property
    def total_purchases(self):
        return self.orders.filter(status='completed').aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0


class SalesOrder(models.Model):
    """Sales orders for fish products."""
    
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PROCESSING = 'processing', 'Processing'
        SHIPPED = 'shipped', 'Shipped'
        DELIVERED = 'delivered', 'Delivered'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    class PaymentStatus(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        PARTIAL = 'partial', 'Partially Paid'
        PAID = 'paid', 'Paid'
    
    order_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='orders')
    harvest_record = models.ForeignKey(
        'harvest.HarvestRecord', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='sales_orders'
    )
    order_date = models.DateField()
    delivery_date = models.DateField(null=True, blank=True)
    quantity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    price_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    delivery_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = (self.quantity_kg * self.price_per_kg) - self.discount
        super().save(*args, **kwargs)


class Payment(models.Model):
    """Payment records for sales orders."""
    
    class Method(models.TextChoices):
        CASH = 'cash', 'Cash'
        BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
        CHECK = 'check', 'Check'
        CREDIT = 'credit', 'Credit'
    
    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    payment_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True)
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.order.order_number} - {self.amount}"
