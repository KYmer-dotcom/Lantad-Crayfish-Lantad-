"""
SALES MODULE - Serializers
"""

from rest_framework import serializers
from .models import Customer, SalesOrder, Payment


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for Customer model."""
    
    customer_type_display = serializers.CharField(source='get_customer_type_display', read_only=True)
    total_purchases = serializers.ReadOnlyField()
    
    class Meta:
        model = Customer
        fields = ['id', 'name', 'customer_type', 'customer_type_display',
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
        fields = ['id', 'order_number', 'customer', 'customer_name', 'harvest_record',
                  'order_date', 'delivery_date', 'quantity_kg', 'price_per_kg',
                  'total_amount', 'discount', 'status', 'status_display',
                  'payment_status', 'payment_status_display', 'delivery_address',
                  'notes', 'created_by', 'created_by_name', 'payments',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
