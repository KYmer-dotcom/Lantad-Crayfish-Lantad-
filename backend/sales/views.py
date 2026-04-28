"""
SALES MODULE - Views
"""

from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Customer, SalesOrder, Payment
from .serializers import CustomerSerializer, SalesOrderSerializer, PaymentSerializer


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
