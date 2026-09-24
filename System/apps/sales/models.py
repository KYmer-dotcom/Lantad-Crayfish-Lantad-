"""
=============================================================================
SALES MODULE - Sales and Product Distribution Monitoring
=============================================================================
Manages customers, sales orders, and delivery tracking.
=============================================================================
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


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
        return self.orders.filter(
            status__in=[SalesOrder.Status.COMPLETED, SalesOrder.Status.DELIVERED]
        ).aggregate(
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

    class UnitType(models.TextChoices):
        PCS = 'pcs', 'Pieces (pcs)'
        KG = 'kg', 'Kilograms (kg)'
        TUB = 'tub', 'Tubs'
        PAIR = 'pair', 'Pairs'
        PACK = 'pack', 'Packs'
        HEAD = 'head', 'Heads'

    name = models.CharField(max_length=200)
    species = models.ForeignKey('stock.Species', on_delete=models.SET_NULL, null=True, blank=True)
    pond = models.ForeignKey('operations.Pond', on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.FISH)
    accent_color = models.CharField(max_length=20, default='indigo')
    icon = models.CharField(max_length=20, default='fish')
    unit_type = models.CharField(max_length=20, choices=UnitType.choices, default=UnitType.PCS, help_text="Measurement unit for this product")
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
    def unit_display(self):
        return self.unit_type or 'pcs'

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

    @property
    def payment_method_display(self):
        notes = (self.notes or '').strip()
        if not notes:
            return 'Cash' if (self.delivery_address or '').upper() == 'PICKUP' else 'Cash on Delivery'
        notes_lower = notes.lower()
        if 'gcash' in notes_lower:
            return 'GCash'
        if 'cash on delivery' in notes_lower or 'cod' in notes_lower:
            return 'Cash on Delivery'
        if 'cash' in notes_lower:
            return 'Cash'
        clean = notes.replace('[PC]', '').replace('[KG]', '').replace('Payment:', '').strip()
        if '(Session #' in clean:
            clean = clean.split('(Session #')[0].strip()
        return clean or 'Cash'
    
    def save(self, *args, **kwargs):
        if not self.order_date:
            self.order_date = timezone.now().date()
        if not self.order_number:
            from datetime import date
            today = self.order_date or date.today()
            prefix = f"SO-{today.strftime('%Y%m%d')}"
            count = SalesOrder.objects.filter(order_number__startswith=prefix).count() + 1
            self.order_number = f"{prefix}-{count:04d}"
        if not self.price_per_kg:
            if self.product:
                self.price_per_kg = self.product.price_per_kg or self.product.unit_price or 0
            else:
                self.price_per_kg = 0
        if not self.quantity_kg:
            self.quantity_kg = 1
        if not self.total_amount:
            self.total_amount = (self.quantity_kg * self.price_per_kg) - (self.discount or 0)
        super().save(*args, **kwargs)

        if self.product and not self.stock_deducted and self.status in [self.Status.DELIVERED, self.Status.COMPLETED]:
            from decimal import Decimal
            is_kg = '[KG]' in (self.notes or '')
            deduct_qty = Decimal(str(self.quantity_kg or 0))
            if is_kg and self.product.pieces_per_kg and self.product.pieces_per_kg > 0:
                deduct_qty = deduct_qty * Decimal(str(self.product.pieces_per_kg))

            current_stock = Decimal(str(self.product.quantity_kg or 0))
            self.product.quantity_kg = max(current_stock - deduct_qty, Decimal('0'))
            self.product.save(update_fields=['quantity_kg', 'updated_at'])
            InventoryTransaction.objects.create(
                product=self.product,
                quantity_kg=-deduct_qty,
                transaction_type=InventoryTransaction.Type.SALE,
                related_order=self,
                created_by=self.created_by
            )
            SalesOrder.objects.filter(pk=self.pk).update(stock_deducted=True)
            self.stock_deducted = True


class InventoryTransaction(models.Model):
    """Stock movements for products."""

    class Type(models.TextChoices):
        HARVEST = 'harvest', 'Harvest Inflow'
        SALE = 'sale', 'Sales Deduction'
        ADJUSTMENT = 'adjustment', 'Manual Adjustment'
        MORTALITY = 'mortality', 'Mortality/Loss'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=Type.choices)
    related_order = models.ForeignKey('sales.SalesOrder', on_delete=models.SET_NULL, null=True, blank=True)
    related_harvest = models.ForeignKey('harvest.HarvestRecord', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Inventory Transaction'
        verbose_name_plural = 'Inventory Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.product.name} ({self.quantity_kg:+} kg) - {self.get_transaction_type_display()}"


class Rider(models.Model):
    """Delivery riders / logistics staff."""
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
    address = models.CharField(max_length=255, blank=True)
    license_evidence = models.ImageField(upload_to='rider_licenses/', null=True, blank=True)
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
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
    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    quantity_kg = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED)
    proof_of_delivery = models.ImageField(upload_to='proof_of_delivery/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Delivery'
        verbose_name_plural = 'Deliveries'
        ordering = ['-scheduled_date']

    def __str__(self):
        return f"{self.order.order_number} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if not self.scheduled_date:
            self.scheduled_date = (self.order.order_date if self.order and self.order.order_date else timezone.now().date())
        if not self.quantity_kg:
            self.quantity_kg = (self.order.quantity_kg if self.order else 1)
        if not self.delivery_location:
            self.delivery_location = (self.order.delivery_address if self.order and self.order.delivery_address else 'Customer Address')
        super().save(*args, **kwargs)


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


class InputLog(models.Model):
    """Audit trail tracking who added or deleted data across the system."""
    class Action(models.TextChoices):
        ADDED = 'added', 'Added Data'
        DELETED = 'deleted', 'Deleted Data'
        UPDATED = 'updated', 'Updated Data'
        CREATE = 'create', 'Created Data'

    class Category(models.TextChoices):
        SALES = 'Sales Orders', 'Sales'
        INVENTORY = 'Inventory', 'Inventory'
        OPERATIONS = 'Operations', 'Operations'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    user_name = models.CharField(max_length=150)
    user_role = models.CharField(max_length=50, default='Owner')
    action = models.CharField(max_length=20, choices=Action.choices, default=Action.ADDED)
    module = models.CharField(max_length=100, default='Sales Orders')
    target_entity = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Input Log'
        verbose_name_plural = 'Input Logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_action_display()}] {self.target_entity} by {self.user_name}"

    @property
    def category(self):
        return self.module

    @classmethod
    def log(cls, user=None, action=Action.ADDED, module='Sales Orders', target_entity='', details="", **kwargs):
        if 'category' in kwargs:
            module = str(kwargs.pop('category'))
        if 'target' in kwargs:
            target_entity = kwargs.pop('target')

        user_name = 'System Admin'
        user_role = 'Admin'
        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            user_name = user.get_full_name() or user.username
            user_role = getattr(user, 'role', 'User').capitalize()
        elif user and hasattr(user, 'username'):
            user_name = user.get_full_name() or user.username
            user_role = getattr(user, 'role', 'User').capitalize()

        return cls.objects.create(
            user=user if (user and hasattr(user, 'pk') and user.pk) else None,
            user_name=user_name,
            user_role=user_role,
            action=action,
            module=module,
            target_entity=target_entity,
            details=details,
            created_at=timezone.now()
        )


