from django.test import TestCase
from decimal import Decimal
from datetime import date
from apps.feed.models import FeedType, FeedInventory, FeedStockMovement

class FeedInventoryTest(TestCase):
    def test_feed_type_creation_and_fields(self):
        ft = FeedType.objects.create(
            name='Integra 1000 Starter',
            category=FeedType.Category.STARTER,
            protein_content=Decimal('40.0'),
            price_per_kg=Decimal('85.00')
        )
        self.assertEqual(ft.name, 'Integra 1000 Starter')
        self.assertEqual(ft.category, FeedType.Category.STARTER)
        self.assertEqual(ft.protein_content, Decimal('40.0'))

    def test_feed_inventory_creation(self):
        ft = FeedType.objects.create(
            name='Grower Pellet PO2',
            category=FeedType.Category.GROWER,
            protein_content=Decimal('35.0'),
            price_per_kg=Decimal('75.00')
        )
        inv = FeedInventory.objects.create(
            feed_type=ft,
            quantity_kg=Decimal('500.00'),
            purchase_date=date(2026, 1, 10),
            total_cost=Decimal('37500.00')
        )
        self.assertEqual(inv.quantity_kg, Decimal('500.00'))
        self.assertEqual(inv.total_cost, Decimal('37500.00'))

    def test_feed_stock_movement_ledger(self):
        ft = FeedType.objects.create(
            name='Finisher Pellet PO3',
            category=FeedType.Category.FINISHER,
            protein_content=Decimal('30.0'),
            price_per_kg=Decimal('65.00')
        )
        mov = FeedStockMovement.objects.create(
            feed_type=ft,
            movement_type=FeedStockMovement.MovementType.IN,
            delta_kg=Decimal('100.00'),
            notes='Delivery from supplier'
        )
        self.assertEqual(mov.movement_type, FeedStockMovement.MovementType.IN)
        self.assertEqual(FeedStockMovement.available_stock(ft), Decimal('100.00'))
