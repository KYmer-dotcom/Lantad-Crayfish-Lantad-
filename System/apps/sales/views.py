from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from apps.accounts.access import is_owner, is_customer, get_customer_profile
from .models import Customer, Product, SalesOrder, InventoryTransaction, Delivery, PaymentSetting
from .serializers import (
    CustomerSerializer,
    ProductSerializer,
    SalesOrderSerializer,
    PaymentSettingSerializer,
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
        user = self.request.user
        if is_owner(user):
            return Customer.objects.all()
        customer = get_customer_profile(user)
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
        user = self.request.user
        if is_owner(user):
            return SalesOrder.objects.select_related('customer', 'created_by', 'harvest_record').all()
        customer = get_customer_profile(user)
        if customer:
            return SalesOrder.objects.select_related('customer', 'created_by', 'harvest_record').filter(
                customer=customer
            )
        return SalesOrder.objects.none()

    @action(detail=True, methods=['post'], url_path='update-payment')
    def update_payment(self, request, pk=None):
        """Update payment status for an order via REST API."""
        order = self.get_object()
        new_status = request.data.get('payment_status')
        if new_status in [c[0] for c in SalesOrder.PaymentStatus.choices]:
            order.payment_status = new_status
            order.save(update_fields=['payment_status', 'updated_at'])
            return Response({'success': True, 'payment_status': order.payment_status})
        return Response({'success': False, 'error': 'Invalid payment_status'}, status=status.HTTP_400_BAD_REQUEST)


class PaymentSettingViewSet(viewsets.ModelViewSet):
    """
    CRUD / settings for GCash and PayMongo payments.
    """
    
    queryset = PaymentSetting.objects.all()
    serializer_class = PaymentSettingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PaymentSetting.objects.all()


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
        user = self.request.user
        if is_owner(user):
            return Product.objects.select_related('species', 'pond').all()
        return Product.objects.filter(is_active=True).select_related('species', 'pond')


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
        user = self.request.user
        if is_owner(user):
            return InventoryTransaction.objects.select_related('product', 'created_by').all()
        return InventoryTransaction.objects.none()


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
        user = self.request.user
        if is_owner(user):
            return Delivery.objects.select_related('order', 'created_by').all()
        customer = get_customer_profile(user)
        if customer:
            return Delivery.objects.select_related('order', 'created_by').filter(
                order__customer=customer
            )
        return Delivery.objects.none()
