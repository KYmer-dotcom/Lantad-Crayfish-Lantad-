from django.test import TestCase
from decimal import Decimal
from datetime import date
from django.contrib.auth import get_user_model
from apps.operations.models import Farm, Pond
from apps.stock.models import Species, StockBatch
from apps.harvest.models import HarvestSchedule, HarvestRecord

User = get_user_model()

class HarvestForecastingTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='harvestowner', email='harvest@lantad.com', password='password123', role='owner')
        self.farm = Farm.objects.create(name='Harvest Farm', location='Silay', total_area=Decimal('3000.00'), owner=self.owner)
        self.pond = Pond.objects.create(farm=self.farm, name='Harvest Pond', size=Decimal('200.00'), depth=Decimal('1.5'), capacity=4000)
        self.species = Species.objects.create(name='Red Claw Crayfish', category=Species.Category.CRUSTACEANS)
        self.batch = StockBatch.objects.create(
            pond=self.pond,
            species=self.species,
            batch_code='BATCH-HARV-001',
            stocking_date=date(2026, 1, 1),
            initial_quantity=2000,
            current_quantity=1900,
            initial_average_weight=Decimal('5.00'),
            current_average_weight=Decimal('55.00')
        )

    def test_harvest_schedule_creation(self):
        sched = HarvestSchedule.objects.create(
            stock_batch=self.batch,
            scheduled_date=date(2026, 4, 15),
            estimated_quantity=1800,
            estimated_total_weight=Decimal('99.00'),
            target_weight=Decimal('55.00'),
            status=HarvestSchedule.Status.SCHEDULED
        )
        self.assertEqual(sched.status, HarvestSchedule.Status.SCHEDULED)
        self.assertEqual(sched.estimated_quantity, 1800)

    def test_harvest_record_creation(self):
        rec = HarvestRecord.objects.create(
            stock_batch=self.batch,
            harvest_date=date(2026, 4, 15),
            quantity_harvested=1850,
            total_weight_kg=Decimal('101.75'),
            average_weight_per_fish=Decimal('55.00'),
            grade_a_quantity=1500,
            grade_b_quantity=350
        )
        self.assertEqual(rec.quantity_harvested, 1850)
        self.assertEqual(rec.total_weight_kg, Decimal('101.75'))
        self.assertEqual(rec.grade_a_quantity + rec.grade_b_quantity, 1850)
