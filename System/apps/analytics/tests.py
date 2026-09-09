"""
White-Box Unit Tests for Analytics & Algorithmic Services (Pillar 2)
"""
from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.analytics.predictive_services import (
    linear_regression_trend,
    forecast_sales_moving_average,
    get_product_recommendations
)
from apps.sales.models import Product, Customer, SalesOrder

User = get_user_model()


class AlgorithmicServicesTestCase(TestCase):
    """
    White-Box Unit Tests for Business Logic, Predictive Models, and Analytics
    """

    def test_tc_wlogic006_linear_regression_trend(self):
        """TC-WLogic006: Linear regression slope, intercept, and directional trend calculation."""
        # Test Case A: Upward trend
        upward_sales = [
            {'date': date(2026, 3, 1), 'revenue': 1000.0},
            {'date': date(2026, 3, 2), 'revenue': 1500.0},
            {'date': date(2026, 3, 3), 'revenue': 2000.0},
            {'date': date(2026, 3, 4), 'revenue': 2500.0},
            {'date': date(2026, 3, 5), 'revenue': 3000.0},
        ]
        result_up = linear_regression_trend(upward_sales)
        self.assertEqual(result_up['trend'], 'increasing')
        self.assertEqual(result_up['slope'], 500.0)
        self.assertEqual(result_up['intercept'], 1000.0)

        # Test Case B: Flat / insufficient trend
        flat_sales = [{'date': date(2026, 3, 1), 'revenue': 1000.0}]
        result_flat = linear_regression_trend(flat_sales)
        self.assertEqual(result_flat['trend'], 'flat')
        self.assertEqual(result_flat['slope'], 0)

    def test_tc_wlogic007_moving_average_forecast(self):
        """TC-WLogic007: 7-day rolling moving average forward multi-day sales forecast."""
        daily_sales = [
            {'date': date(2026, 3, 1), 'revenue': 100.0},
            {'date': date(2026, 3, 2), 'revenue': 200.0},
            {'date': date(2026, 3, 3), 'revenue': 300.0},
            {'date': date(2026, 3, 4), 'revenue': 400.0},
            {'date': date(2026, 3, 5), 'revenue': 500.0},
            {'date': date(2026, 3, 6), 'revenue': 600.0},
            {'date': date(2026, 3, 7), 'revenue': 700.0},
        ]
        predictions = forecast_sales_moving_average(daily_sales, days_to_predict=3, window_size=7)

        self.assertEqual(len(predictions), 3)
        # Average of 100..700 is 2800 / 7 = 400.0
        self.assertEqual(predictions[0]['date'], date(2026, 3, 8))
        self.assertEqual(predictions[0]['predicted_revenue'], 400.0)

        # Next window includes 200..700, 400 -> sum = 3100 / 7 = 442.86
        self.assertEqual(predictions[1]['date'], date(2026, 3, 9))
        self.assertAlmostEqual(predictions[1]['predicted_revenue'], 442.86, places=2)

    def test_tc_wlogic008_product_recommendations(self):
        """TC-WLogic008: Personalized customer product recommendation engine."""
        cust_user = User.objects.create_user(username='rec_cust', password='Password123!', role=User.Role.CUSTOMER)
        customer = Customer.objects.create(name='Recommendation Client', phone='09112233445', user=cust_user)

        prod_crayfish = Product.objects.create(name='Live Red Claw Crayfish (Growout)', quantity_kg=100, price_per_kg=750)
        prod_superworm = Product.objects.create(name='Superworm Live Stock (1kg Tub)', quantity_kg=150, price_per_kg=400)
        prod_breeder = Product.objects.create(name='Crayfish Breeder Pairs (Adult)', quantity_kg=50, price_per_kg=1200)

        # Create sales orders
        SalesOrder.objects.create(
            order_number='SO-REC-001', customer=customer, product=prod_crayfish,
            order_date=date(2026, 3, 1), quantity_kg=5, price_per_kg=750, total_amount=3750, status=SalesOrder.Status.COMPLETED
        )
        SalesOrder.objects.create(
            order_number='SO-REC-002', customer=customer, product=prod_crayfish,
            order_date=date(2026, 3, 2), quantity_kg=10, price_per_kg=750, total_amount=7500, status=SalesOrder.Status.COMPLETED
        )

        user_sales = SalesOrder.objects.filter(customer=customer)
        all_sales = SalesOrder.objects.all()

        recs = get_product_recommendations(user_sales, all_sales)
        self.assertTrue(len(recs) >= 1)
        self.assertEqual(recs[0]['product'], prod_crayfish.name)
        self.assertIn('High reorder potential', recs[0]['reason'])

    def test_tc_wlogic009_low_stock_boundary_evaluation(self):
        """TC-WLogic009: Product is_low_stock threshold boundary predicate."""
        product = Product.objects.create(
            name='Test Superworm Pupae',
            quantity_kg=25.0,
            reorder_level_kg=20.0,
            price_per_kg=500.0
        )
        # Above reorder level
        self.assertFalse(product.is_low_stock)

        # At reorder level
        product.quantity_kg = 20.0
        self.assertTrue(product.is_low_stock)

        # Below reorder level
        product.quantity_kg = 15.0
        self.assertTrue(product.is_low_stock)

    def test_tc_wlogic010_order_amount_and_dual_pricing(self):
        """TC-WLogic010: SalesOrder automatic total amount derivation and discount handling."""
        customer = Customer.objects.create(name='Pricing Client', phone='09112233446')
        product = Product.objects.create(name='Crayfish Juveniles', quantity_kg=50, price_per_kg=600, pieces_per_kg=20)

        # Case: 5 kg at 600 PHP/kg with 200 PHP discount
        order = SalesOrder(
            order_number='SO-PRICE-001',
            customer=customer,
            product=product,
            order_date=date(2026, 3, 1),
            quantity_kg=5.0,
            price_per_kg=600.0,
            discount=200.0
        )
        order.save()

        # Expected: (5 * 600) - 200 = 2800.00
        self.assertEqual(order.total_amount, 2800.00)
