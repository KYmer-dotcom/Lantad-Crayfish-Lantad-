from django.contrib import admin
from .models import Customer, Product, SalesOrder, Delivery, Rider, PaymentSetting, InputLog, InventoryTransaction


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer_type', 'phone', 'email', 'is_active', 'created_at')
    search_fields = ('name', 'phone', 'email', 'address')
    list_filter = ('customer_type', 'is_active')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit_type', 'unit_price', 'price_per_kg', 'quantity_kg', 'is_active', 'created_at')
    search_fields = ('name', 'notes')
    list_filter = ('is_active', 'unit_type', 'category')


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'product', 'quantity_kg', 'total_amount', 'status', 'payment_status', 'order_date')
    search_fields = ('order_number', 'customer__name', 'product__name')
    list_filter = ('status', 'payment_status')


@admin.register(Rider)
class RiderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'vehicle_type', 'plate_number', 'status', 'is_active')
    search_fields = ('name', 'phone', 'plate_number')
    list_filter = ('status', 'is_active', 'vehicle_type')


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'rider', 'status', 'quantity_kg', 'scheduled_date', 'delivered_date')
    search_fields = ('order__order_number', 'rider__name', 'delivery_location')
    list_filter = ('status', 'scheduled_date')


@admin.register(PaymentSetting)
class PaymentSettingAdmin(admin.ModelAdmin):
    list_display = ('gcash_name', 'gcash_number', 'is_gcash_enabled', 'is_cod_enabled', 'updated_at')


@admin.register(InputLog)
class InputLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'module', 'target_entity', 'user_name', 'user_role', 'created_at')
    search_fields = ('action', 'module', 'target_entity', 'details', 'user_name')
    list_filter = ('action', 'module', 'created_at')


@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ('product', 'transaction_type', 'quantity_kg', 'created_at')
    search_fields = ('product__name', 'notes')
    list_filter = ('transaction_type', 'created_at')
