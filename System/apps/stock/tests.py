from django.test import TestCase
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from apps.operations.models import Farm, Pond
from apps.stock.models import Species, StockBatch, SpeciesStock

User = get_user_model()

class SpeciesModelTest(TestCase):
    def test_species_creation_and_defaults(self):
        sp = Species.objects.create(name='Red Claw Crayfish', scientific_name='Cherax quadricarinatus', category=Species.Category.CRUSTACEANS)
        self.assertEqual(sp.name, 'Red Claw Crayfish')
        self.assertEqual(sp.category, Species.Category.CRUSTACEANS)

    def test_species_string_representation(self):
        sp = Species.objects.create(name='Giant Superworm', category=Species.Category.CRUSTACEANS)
        self.assertIn('Giant Superworm', str(sp))

class StockBatchModelTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='batchowner', email='batch@lantad.com', password='password123', role='owner')
        self.farm = Farm.objects.create(name='Batch Farm', location='Silay', total_area=Decimal('2000.00'), owner=self.owner)
        self.pond = Pond.objects.create(farm=self.farm, name='Batch Pond 1', size=Decimal('100.00'), depth=Decimal('1.5'), capacity=5000)
        self.species = Species.objects.create(name='Red Claw Crayfish', category=Species.Category.CRUSTACEANS)

    def test_stock_batch_creation_and_lifecycle(self):
        batch = StockBatch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_code='BATCH-2026-001',
            stocking_date=date(2026, 1, 15),
            initial_quantity=5000,
            current_quantity=4800,
            initial_average_weight=Decimal('5.00'),
            current_average_weight=Decimal('25.50'),
            stage=StockBatch.Stage.JUVENILE
        )
        self.assertEqual(batch.batch_code, 'BATCH-2026-001')
        self.assertEqual(batch.current_quantity, 4800)
        self.assertTrue(batch.is_active)

    def test_stock_batch_survival_rate_computation(self):
        batch = StockBatch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_code='BATCH-2026-002',
            stocking_date=date(2026, 2, 1),
            initial_quantity=1000,
            current_quantity=950,
            initial_average_weight=Decimal('5.00'),
            current_average_weight=Decimal('30.00')
        )
        survival_rate = (batch.current_quantity / batch.initial_quantity) * 100
        self.assertEqual(survival_rate, 95.0)

class SpeciesStockAggregationTest(TestCase):
    def setUp(self):
        self.species = Species.objects.create(name='Superworm', category=Species.Category.CRUSTACEANS)

    def test_species_stock_tracking(self):
        stock = SpeciesStock.objects.create(
            species=self.species,
            available_quantity=8500
        )
        self.assertEqual(stock.available_quantity, 8500)
