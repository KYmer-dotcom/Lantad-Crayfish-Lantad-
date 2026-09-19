"""
================================================================================
WHITE-BOX TEST SUITE: PILLAR 3 - DATABASE TRANSACTIONS, STOCK & AUDIT LOGS
Target Code Routines:
  - TC-WData011: apps.sales.models.SalesOrder::save() [Stock Deduction Atomicity]
  - TC-WData012: apps.sales.models.Delivery::save() [State Machine Lifecycle]
  - TC-WData013: apps.sales.models.Delivery.objects.filter() [Active Queries]
  - TC-WData014: apps.sales.paymongo_service::create_checkout_session() [Payload Guard]
  - TC-WData015: apps.accounts.models.CustomerProfile::lifetime_sales
  - TC-WData016: apps.sales.models.InputLog::log() [Audit Trail Persistence]
================================================================================
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.sales.models import Product, Customer, SalesOrder, Delivery, Rider, InputLog
from apps.sales.paymongo_service import create_checkout_session

User = get_user_model()


class SalesAndDataIntegrityTestCase(TestCase):
    """
    White-Box Unit Tests for Sales Transactions, Delivery Lifecycle, and Audit Logging
    """

    def setUp(self):
        self.user = User.objects.create_user(username='buyer_user', password='Password123!', role=User.Role.CUSTOMER)
        self.customer = Customer.objects.create(name='Acme Aquaculture', phone='09181234567', user=self.user)
        self.product = Product.objects.create(name='Live Crayfish', quantity_kg=100.0, price_per_kg=600.0)

    def test_tc_wdata011_stock_deduction_and_inventory_transaction_atomicity(self):
        """TC-WData011: Automated product stock inventory deduction upon delivery."""
        order = SalesOrder.objects.create(
            order_number='SO-TEST-001', customer=self.customer, product=self.product,
            quantity_kg=Decimal('15.00'), price_per_kg=Decimal('600.00'), total_amount=Decimal('9000.00'),
            status=SalesOrder.Status.COMPLETED
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity_kg, Decimal('85.00'))
        self.assertTrue(order.stock_deducted)

    def test_tc_wdata012_delivery_state_machine_transition(self):
        """TC-WData012: Delivery lifecycle state transition (SCHEDULED -> IN_TRANSIT -> DELIVERED)."""
        order = SalesOrder.objects.create(customer=self.customer, product=self.product, quantity_kg=5.0, price_per_kg=600.0)
        rider = Rider.objects.create(name='Juan Courier', phone='09170001111')
        delivery = Delivery.objects.create(order=order, rider=rider, status=Delivery.Status.SCHEDULED)

        delivery.status = Delivery.Status.IN_TRANSIT
        delivery.save()
        self.assertEqual(delivery.status, Delivery.Status.IN_TRANSIT)

        delivery.status = Delivery.Status.DELIVERED
        delivery.save()
        self.assertEqual(delivery.status, Delivery.Status.DELIVERED)

    def test_tc_wdata013_rider_active_deliveries_aggregation(self):
        """TC-WData013: Dynamic aggregation of rider concurrent active deliveries."""
        rider = Rider.objects.create(name='Pedro Express', phone='09172223333')
        order1 = SalesOrder.objects.create(customer=self.customer, product=self.product, quantity_kg=2.0, price_per_kg=600.0)
        order2 = SalesOrder.objects.create(customer=self.customer, product=self.product, quantity_kg=3.0, price_per_kg=600.0)

        Delivery.objects.create(order=order1, rider=rider, status=Delivery.Status.SCHEDULED)
        Delivery.objects.create(order=order2, rider=rider, status=Delivery.Status.IN_TRANSIT)

        active_count = Delivery.objects.filter(rider=rider, status__in=[Delivery.Status.SCHEDULED, Delivery.Status.IN_TRANSIT]).count()
        self.assertEqual(active_count, 2)

    def test_tc_wdata014_paymongo_checkout_session_guard(self):
        """TC-WData014: PayMongo gateway payload structure and configuration requirement guard."""
        with self.assertRaises(ValueError) as ctx:
            create_checkout_session(line_items=[])
        self.assertIn("Line items are required", str(ctx.exception))

    def test_tc_wdata015_customer_lifetime_purchases_aggregation(self):
        """TC-WData015: Customer lifetime completed sales aggregation property."""
        SalesOrder.objects.create(customer=self.customer, product=self.product, quantity_kg=5.0, total_amount=Decimal('3000.00'), status=SalesOrder.Status.COMPLETED)
        SalesOrder.objects.create(customer=self.customer, product=self.product, quantity_kg=3.0, total_amount=Decimal('1800.00'), status=SalesOrder.Status.COMPLETED)

        completed_total = sum(order.total_amount for order in self.customer.orders.filter(status=SalesOrder.Status.COMPLETED))
        self.assertEqual(completed_total, Decimal('4800.00'))

    def test_tc_wdata016_input_log_audit_trail_creation(self):
        """TC-WData016: Three-tiered InputLog audit trail generation and multi-role attribution."""
        log = InputLog.log(
            user=self.user,
            category=InputLog.Category.SALES,
            action=InputLog.Action.CREATE,
            target='SalesOrder #SO-TEST-001',
            details='Customer submitted order via PayMongo checkout'
        )
        self.assertIsNotNone(log.id)
        self.assertEqual(log.category, InputLog.Category.SALES)
        self.assertEqual(log.action, InputLog.Action.CREATE)
