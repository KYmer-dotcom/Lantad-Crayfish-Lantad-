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
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='customer_profile'
    )
    name = models.CharField(max_length=200)
    customer_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INDIVIDUAL)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField()
    map_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    map_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
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

    @property
    def product_types_count(self):
        return self.orders.values('product').distinct().count()


class Product(models.Model):
    """Products available for sale in the market."""

    class Category(models.TextChoices):
        FISH = 'fish', 'Fish'
        SHRIMP = 'shrimp', 'Shrimp'

    name = models.CharField(max_length=200)
    species = models.ForeignKey('stock.Species', on_delete=models.SET_NULL, null=True, blank=True)
    pond = models.ForeignKey('operations.Pond', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.FISH)
    accent_color = models.CharField(max_length=20, default='indigo')
    icon = models.CharField(max_length=20, default='fish')
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reorder_level_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    price_per_kg = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    pieces_per_kg = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    placement_date = models.DateField(null=True, blank=True)  # Date product placed in stock

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_low_stock(self):
        return self.quantity_kg <= self.reorder_level_kg


class SalesOrder(models.Model):
    """Sales orders for fish products."""

    class OrderType(models.TextChoices):
        RETAIL = 'retail', 'Retail'
        WHOLESALE = 'wholesale', 'Wholesale'

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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
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
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.RETAIL)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.UNPAID)
    receipt_image = models.BinaryField(blank=True, null=True)
    delivery_address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    stock_deducted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sales Order'
        verbose_name_plural = 'Sales Orders'
        ordering = ['-order_date', '-created_at']
    
    def __str__(self):
        return f"{self.order_number} - {self.customer.name}"
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = (self.quantity_kg * self.price_per_kg) - self.discount
        super().save(*args, **kwargs)

        if self.product and not self.stock_deducted and self.status in [self.Status.DELIVERED, self.Status.COMPLETED]:
            is_kg = '[KG]' in (self.notes or '')
            deduct_qty = self.quantity_kg
            if is_kg and self.product.pieces_per_kg and self.product.pieces_per_kg > 0:
                deduct_qty = self.quantity_kg * self.product.pieces_per_kg

            self.product.quantity_kg = max(self.product.quantity_kg - deduct_qty, 0)
            self.product.save(update_fields=['quantity_kg', 'updated_at'])
            InventoryTransaction.objects.create(
                product=self.product,
                quantity_kg=-deduct_qty,
                transaction_type=InventoryTransaction.Type.SALE,
                related_order=self,
                created_by=self.created_by
            )
            SalesOrder.objects.filter(pk=self.pk).update(stock_deducted=True)


class InventoryTransaction(models.Model):
    """Stock movements for products."""

    class Type(models.TextChoices):
        STOCK_IN = 'stock_in', 'Stock In'
        SALE = 'sale', 'Sale'
        ADJUSTMENT = 'adjustment', 'Adjustment'
        TRANSFER = 'transfer', 'Transfer'
        RESTOCK_REQUEST = 'restock_request', 'Restock Request'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=30, choices=Type.choices)
    related_order = models.ForeignKey('sales.SalesOrder', on_delete=models.SET_NULL, null=True, blank=True)
    related_harvest = models.ForeignKey('harvest.HarvestRecord', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} ({self.transaction_type})"


class Rider(models.Model):
    """Delivery rider / driver."""
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        ON_DELIVERY = 'on_delivery', 'On Delivery'
        OFF_DUTY = 'off_duty', 'Off Duty'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='rider_profile'
    )
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=50, default='Motorcycle')
    plate_number = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rider'
        verbose_name_plural = 'Riders'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    @property
    def active_deliveries_count(self):
        return self.deliveries.filter(status__in=[Delivery.Status.SCHEDULED, Delivery.Status.IN_TRANSIT]).count()


class Delivery(models.Model):
    """Delivery records for orders."""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_TRANSIT = 'in_transit', 'In Transit'
        DELIVERED = 'delivered', 'Delivered'
        CANCELLED = 'cancelled', 'Cancelled'

    order = models.ForeignKey(SalesOrder, on_delete=models.CASCADE, related_name='deliveries')
    rider = models.ForeignKey(Rider, on_delete=models.SET_NULL, null=True, blank=True, related_name='deliveries')
    scheduled_date = models.DateField()
    delivered_date = models.DateField(null=True, blank=True)
    delivery_location = models.CharField(max_length=255)
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"


class PaymentSetting(models.Model):
    """Store owner payment destination and gateway settings."""
    gcash_name = models.CharField(max_length=150, default="SILAY SUPERWORM & CRAYFISH")
    gcash_number = models.CharField(max_length=30, default="09171234567")
    gcash_qr_image = models.ImageField(upload_to='payment_qr/', null=True, blank=True)
    is_gcash_enabled = models.BooleanField(default=True)
    is_cod_enabled = models.BooleanField(default=True)
    paymongo_public_key = models.CharField(max_length=150, blank=True)
    paymongo_secret_key = models.CharField(max_length=150, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment Setting'
        verbose_name_plural = 'Payment Settings'

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj

    def __str__(self):
        return f"Payment Setting ({self.gcash_number})"


