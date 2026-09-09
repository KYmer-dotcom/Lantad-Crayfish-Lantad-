"""
White-Box Unit Tests for Sales, Deliveries, Product Stock Inventory, and Audit Logging (Pillar 3)
"""
from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.sales.models import (
    Customer,
    Product,
    SalesOrder,
    Delivery,
    Rider,
    InventoryTransaction,
    InputLog,
    PaymentSetting
)
from apps.sales.paymongo_service import create_paymongo_checkout_session

User = get_user_model()


class SalesAndDataIntegrityTestCase(TestCase):
    """
    White-Box Unit Tests for Database Transactions, Inventory Deductions, and State Machines
    """

    def setUp(self):
        self.owner = User.objects.create_user(
            username='admin_owner', password='Password123!', role=User.Role.OWNER
        )
        self.customer = Customer.objects.create(
            name='Aquaculture Wholesale Hub',
            phone='09181234567',
            address='Silay City, Negros Occidental'
        )
        self.rider_user = User.objects.create_user(
            username='rider_01', password='Password123!', role=User.Role.RIDER
        )
        self.rider = Rider.objects.create(
            name='Juan Rider',
            phone='09170001111',
            user=self.rider_user,
            vehicle_type='Motorcycle (Plate: NW-4421)'
        )
        self.product = Product.objects.create(
            name='Superworm Large Larvae',
            quantity_kg=Decimal('100.00'),
            reorder_level_kg=Decimal('20.00'),
            price_per_kg=Decimal('450.00'),
            pieces_per_kg=Decimal('1.00')
        )

    def test_tc_wdata011_stock_deduction_and_inventory_transaction_atomicity(self):
        """TC-WData011: Automated product stock inventory deduction and transaction ledger creation upon delivery."""
        order = SalesOrder.objects.create(
            order_number='SO-DEDUCT-001',
            customer=self.customer,
            product=self.product,
            order_date=date(2026, 3, 1),
            quantity_kg=Decimal('15.00'),
            price_per_kg=Decimal('450.00'),
            status=SalesOrder.Status.PENDING,
            created_by=self.owner
        )

        # Before delivery, stock is 100.00 kg and not deducted
        self.assertEqual(self.product.quantity_kg, Decimal('100.00'))
        self.assertFalse(order.stock_deducted)

        # Transition order to DELIVERED
        order.status = SalesOrder.Status.DELIVERED
        order.save()

        # Reload product and order from DB
        self.product.refresh_from_db()
        order.refresh_from_db()

        self.assertEqual(self.product.quantity_kg, Decimal('85.00'))
        self.assertTrue(order.stock_deducted)

        # Verify InventoryTransaction ledger entry
        tx = InventoryTransaction.objects.filter(related_order=order).first()
        self.assertIsNotNone(tx)
        self.assertEqual(tx.quantity_kg, Decimal('-15.00'))
        self.assertEqual(tx.transaction_type, InventoryTransaction.Type.SALE)

    def test_tc_wdata012_delivery_state_machine_transition(self):
        """TC-WData012: Delivery lifecycle state transition (SCHEDULED -> IN_TRANSIT -> DELIVERED)."""
        order = SalesOrder.objects.create(
            order_number='SO-STATE-001',
            customer=self.customer,
            product=self.product,
            order_date=date(2026, 3, 1),
            quantity_kg=Decimal('10.00'),
            price_per_kg=Decimal('450.00')
        )
        delivery = Delivery.objects.create(
            order=order,
            rider=self.rider,
            scheduled_date=date(2026, 3, 2),
            delivery_location='Silay Port Road',
            quantity_kg=Decimal('10.00'),
            status=Delivery.Status.SCHEDULED
        )

        self.assertEqual(delivery.status, Delivery.Status.SCHEDULED)

        # Transition to IN_TRANSIT
        delivery.status = Delivery.Status.IN_TRANSIT
        delivery.save()
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, Delivery.Status.IN_TRANSIT)

        # Transition to DELIVERED
        delivery.status = Delivery.Status.DELIVERED
        delivery.delivered_date = date(2026, 3, 2)
        delivery.save()
        delivery.refresh_from_db()
        self.assertEqual(delivery.status, Delivery.Status.DELIVERED)

    def test_tc_wdata013_rider_active_deliveries_aggregation(self):
        """TC-WData013: Dynamic aggregation of rider concurrent active deliveries."""
        order1 = SalesOrder.objects.create(order_number='SO-ACT-001', customer=self.customer, quantity_kg=5, price_per_kg=450, order_date=date(2026, 3, 1))
        order2 = SalesOrder.objects.create(order_number='SO-ACT-002', customer=self.customer, quantity_kg=8, price_per_kg=450, order_date=date(2026, 3, 1))
        order3 = SalesOrder.objects.create(order_number='SO-ACT-003', customer=self.customer, quantity_kg=12, price_per_kg=450, order_date=date(2026, 3, 1))

        d1 = Delivery.objects.create(order=order1, rider=self.rider, scheduled_date=date(2026, 3, 2), delivery_location='Point A', quantity_kg=5, status=Delivery.Status.SCHEDULED)
        d2 = Delivery.objects.create(order=order2, rider=self.rider, scheduled_date=date(2026, 3, 2), delivery_location='Point B', quantity_kg=8, status=Delivery.Status.IN_TRANSIT)
        d3 = Delivery.objects.create(order=order3, rider=self.rider, scheduled_date=date(2026, 3, 2), delivery_location='Point C', quantity_kg=12, status=Delivery.Status.DELIVERED)

        # Should count SCHEDULED and IN_TRANSIT (2 deliveries)
        self.assertEqual(self.rider.active_deliveries_count, 2)

    def test_tc_wdata014_paymongo_checkout_session_guard(self):
        """TC-WData014: PayMongo gateway payload structure and configuration requirement guard."""
        order = SalesOrder.objects.create(
            order_number='SO-PAY-001',
            customer=self.customer,
            product=self.product,
            order_date=date(2026, 3, 1),
            quantity_kg=Decimal('2.00'),
            price_per_kg=Decimal('450.00'),
            total_amount=Decimal('900.00')
        )
        
        # When secret key is unconfigured or placeholder
        result = create_paymongo_checkout_session(
            orders=[order],
            customer=self.customer,
            success_url='http://localhost:8000/sales/payment/success/',
            cancel_url='http://localhost:8000/sales/payment/cancel/'
        )
        self.assertIn('error', result)
        self.assertIn('PayMongo Secret Key not configured', result['error'])

    def test_tc_wdata015_customer_lifetime_purchases_aggregation(self):
        """TC-WData015: Customer lifetime completed sales aggregation property."""
        self.assertEqual(self.customer.total_purchases, 0)

        SalesOrder.objects.create(
            order_number='SO-CUST-001',
            customer=self.customer,
            product=self.product,
            order_date=date(2026, 3, 1),
            quantity_kg=10,
            price_per_kg=450,
            total_amount=4500,
            status=SalesOrder.Status.COMPLETED
        )
        SalesOrder.objects.create(
            order_number='SO-CUST-002',
            customer=self.customer,
            product=self.product,
            order_date=date(2026, 3, 2),
            quantity_kg=5,
            price_per_kg=450,
            total_amount=2250,
            status=SalesOrder.Status.COMPLETED
        )
        SalesOrder.objects.create(
            order_number='SO-CUST-003',
            customer=self.customer,
            product=self.product,
            order_date=date(2026, 3, 3),
            quantity_kg=20,
            price_per_kg=450,
            total_amount=9000,
            status=SalesOrder.Status.PENDING # Not completed
        )

        self.assertEqual(self.customer.total_purchases, Decimal('6750.00'))

    def test_tc_wdata016_input_log_audit_trail_creation(self):
        """TC-WData016: Three-tiered InputLog audit trail generation and multi-role attribution."""
        log_entry = InputLog.log(
            user=self.owner,
            action=InputLog.Action.ADDED,
            module='Sales Orders',
            target_entity='Order #SO-2026-9901',
            details='New commercial superworm order created (15.00 kg)'
        )

        self.assertEqual(log_entry.user, self.owner)
        self.assertEqual(log_entry.user_role, 'Owner')
        self.assertEqual(log_entry.action, InputLog.Action.ADDED)
        self.assertEqual(log_entry.module, 'Sales Orders')
        self.assertEqual(InputLog.objects.count(), 1)
