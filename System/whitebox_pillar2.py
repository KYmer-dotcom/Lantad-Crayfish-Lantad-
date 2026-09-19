"""
================================================================================
WHITE-BOX TEST SUITE: PILLAR 2 - ALGORITHMIC SERVICES & DEMAND FORECASTING
Target Code Routines:
  - TC-WLogic006: apps.analytics.predictive_services::linear_regression_trend()
  - TC-WLogic007: apps.analytics.predictive_services::forecast_sales_moving_average()
  - TC-WLogic008: apps.analytics.predictive_services::get_product_recommendations()
  - TC-WLogic009: apps.sales.models.Product::is_low_stock
  - TC-WLogic010: apps.sales.models.SalesOrder::save() [Dual Pricing & Totals]
================================================================================
"""
from datetime import date
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
        self.assertEqual(predictions[0]['predicted_revenue'], 400.0)
        self.assertAlmostEqual(predictions[1]['predicted_revenue'], 442.86, places=2)

    def test_tc_wlogic008_product_recommendations(self):
        """TC-WLogic008: Personalized customer product recommendation engine."""
        cust_user = User.objects.create_user(username='rec_cust', password='Password123!', role=User.Role.CUSTOMER)
        customer = Customer.objects.create(name='Client Alpha', phone='09112233445', user=cust_user)
        prod_crayfish = Product.objects.create(name='Live Red Claw Crayfish', quantity_kg=100, price_per_kg=750)

        SalesOrder.objects.create(
            order_number='SO-REC-001', customer=customer, product=prod_crayfish,
            order_date=date(2026, 3, 1), quantity_kg=5, price_per_kg=750, total_amount=3750, status=SalesOrder.Status.COMPLETED
        )
        recs = get_product_recommendations(SalesOrder.objects.filter(customer=customer), SalesOrder.objects.all())
        self.assertEqual(recs[0]['product'], prod_crayfish.name)

    def test_tc_wlogic009_low_stock_boundary_evaluation(self):
        """TC-WLogic009: Product is_low_stock threshold boundary predicate."""
        product = Product.objects.create(name='Superworm Stock', quantity_kg=25.0, reorder_level_kg=20.0, price_per_kg=500.0)
        self.assertFalse(product.is_low_stock)
        product.quantity_kg = 20.0
        self.assertTrue(product.is_low_stock)

    def test_tc_wlogic010_order_amount_and_dual_pricing(self):
        """TC-WLogic010: SalesOrder automatic total amount derivation and discount handling."""
        product = Product.objects.create(name='Breeder Pairs', quantity_kg=50, price_per_kg=600)
        customer = Customer.objects.create(name='Direct Buyer', phone='09199990000')
        order = SalesOrder(customer=customer, product=product, quantity_kg=5.0, price_per_kg=600.0, discount=200.0)
        order.save()
        self.assertEqual(float(order.total_amount), 2800.00)
