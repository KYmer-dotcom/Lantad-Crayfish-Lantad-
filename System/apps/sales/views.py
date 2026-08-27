"""
SALES MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.access import is_owner, is_customer, get_customer_profile
from .models import Customer, Product, SalesOrder, Payment, InventoryTransaction, Delivery
from .serializers import (
    CustomerSerializer,
    ProductSerializer,
    SalesOrderSerializer,
    PaymentSerializer,
    InventoryTransactionSerializer,
    DeliverySerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Customers.
    """
    
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'contact_person', 'phone', 'email']
    ordering_fields = ['name', 'created_at']

    def get_queryset(self):
        if customer:
            return Customer.objects.filter(id=customer.id)
        return Customer.objects.none()


class SalesOrderViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Sales Orders.
    """
    
    queryset = SalesOrder.objects.select_related('customer', 'created_by', 'harvest_record').all()
    serializer_class = SalesOrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['order_number', 'customer__name']
    ordering_fields = ['order_date', 'total_amount', 'created_at']
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        if is_owner(self.request.user):
            return SalesOrder.objects.select_related('customer', 'created_by', 'harvest_record').all()
        if customer:
            return SalesOrder.objects.select_related('customer', 'created_by', 'harvest_record').filter(
                customer=customer
            )
        return SalesOrder.objects.none()


class PaymentViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Payments.
    """
    
    queryset = Payment.objects.select_related('order', 'received_by').all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['payment_date', 'amount', 'created_at']
    
    def perform_create(self, serializer):
        payment = serializer.save(received_by=self.request.user)
        # Update order payment status
        order = payment.order
        total_paid = sum(p.amount for p in order.payments.all())
        if total_paid >= order.total_amount:
            order.payment_status = 'paid'
        elif total_paid > 0:
            order.payment_status = 'partial'
        order.save()

    def get_queryset(self):
        if is_owner(self.request.user):
            return Payment.objects.select_related('order', 'received_by').all()
        if customer:
            return Payment.objects.select_related('order', 'received_by').filter(
                order__customer=customer
            )
        return Payment.objects.none()


class ProductViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Products.
    """

    queryset = Product.objects.select_related('species', 'pond').all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'species__name']
    ordering_fields = ['name', 'quantity_kg', 'updated_at']

    def get_queryset(self):
        if is_owner(self.request.user):
            return Product.objects.select_related('species', 'pond').all()


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Inventory Transactions.
    """

    queryset = InventoryTransaction.objects.select_related('product', 'created_by').all()
    serializer_class = InventoryTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'quantity_kg']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        if is_owner(self.request.user):
            return InventoryTransaction.objects.select_related('product', 'created_by').all()


class DeliveryViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for Deliveries.
    """

    queryset = Delivery.objects.select_related('order', 'created_by').all()
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['scheduled_date', 'delivered_date', 'created_at']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        if is_owner(self.request.user):
            return Delivery.objects.select_related('order', 'created_by').all()
        if customer:
            return Delivery.objects.select_related('order', 'created_by').filter(
                order__customer=customer
            )
        return Delivery.objects.none()
