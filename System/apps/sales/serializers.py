"""
SALES MODULE - Serializers
"""

from rest_framework import serializers
from .models import Customer, Product, SalesOrder, Payment, InventoryTransaction, Delivery


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    customer_type_display = serializers.CharField(source='get_customer_type_display', read_only=True)
    total_purchases = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = ['id', 'user', 'name', 'customer_type', 'customer_type_display',
                  'contact_person', 'phone', 'email', 'address', 'credit_limit',
                  'is_active', 'total_purchases', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    received_by_name = serializers.CharField(source='received_by.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'payment_method_display',
                  'payment_date', 'reference_number', 'received_by', 'received_by_name',
                  'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class SalesOrderSerializer(serializers.ModelSerializer):
    """Serializer for SalesOrder model."""
    
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    
    class Meta:
        model = SalesOrder
        fields = ['id', 'order_number', 'customer', 'customer_name', 'product',
                  'order_type', 'harvest_record',
                  'order_date', 'delivery_date', 'quantity_kg', 'price_per_kg',
                  'total_amount', 'discount', 'status', 'status_display',
                  'payment_status', 'payment_status_display', 'delivery_address',
                  'notes', 'created_by', 'created_by_name', 'payments', 'stock_deducted',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class InventoryTransactionSerializer(serializers.ModelSerializer):
    """Serializer for InventoryTransaction model."""

    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = InventoryTransaction
        fields = ['id', 'product', 'product_name', 'quantity_kg', 'transaction_type',
                  'related_order', 'related_harvest', 'created_by', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class DeliverySerializer(serializers.ModelSerializer):
    """Serializer for Delivery model."""

    order_number = serializers.CharField(source='order.order_number', read_only=True)

    class Meta:
        model = Delivery
        fields = ['id', 'order', 'order_number', 'scheduled_date', 'delivered_date',
                  'delivery_location', 'quantity_kg', 'status', 'created_by', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
class ProductSerializer(serializers.ModelSerializer):
    """Serializer for Product model."""

    species_name = serializers.CharField(source='species.name', read_only=True)
    pond_name = serializers.CharField(source='pond.name', read_only=True)
    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'species', 'species_name', 'pond', 'pond_name',
                  'category', 'quantity_kg', 'reorder_level_kg', 'unit_price',
                  'is_low_stock', 'is_active', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'is_low_stock', 'created_at', 'updated_at']

