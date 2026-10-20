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

    def test_harvest_readiness_indicator(self):
        from datetime import timedelta
        from django.utils import timezone
        from django.template.loader import render_to_string

        today = timezone.localdate()

        # Far pond (transferred 10 days ago, target 150)
        pond_far = Pond.objects.create(
            farm=self.farm, name='Far Pond', location='Main Pond',
            size=Decimal('100.00'), depth=Decimal('1.5'),
            capacity=100, transfer_date=today - timedelta(days=10), status='active'
        )
        self.assertEqual(pond_far.harvest_readiness_status, 'far')
        self.assertEqual(pond_far.harvest_readiness_display, 'Far')

        # Near pond (transferred 130 days ago, target 150, near >= 120)
        pond_near = Pond.objects.create(
            farm=self.farm, name='Near Pond', location='Main Pond',
            size=Decimal('100.00'), depth=Decimal('1.5'),
            capacity=100, transfer_date=today - timedelta(days=130), status='active'
        )
        self.assertEqual(pond_near.harvest_readiness_status, 'near')
        self.assertEqual(pond_near.harvest_readiness_display, 'Near')

        # Ready pond (transferred 155 days ago, target 150)
        pond_ready = Pond.objects.create(
            farm=self.farm, name='Ready Pond', location='Main Pond',
            size=Decimal('100.00'), depth=Decimal('1.5'),
            capacity=100, transfer_date=today - timedelta(days=155), status='active'
        )
        self.assertEqual(pond_ready.harvest_readiness_status, 'ready')
        self.assertEqual(pond_ready.harvest_readiness_display, 'Ready')

        # Render table partial and verify no icons in status badges
        html = render_to_string('harvest_management/partials/schedules_table.html', {
            'schedules': [pond_far, pond_near, pond_ready]
        })
        self.assertIn('Far', html)
        self.assertIn('Near', html)
        self.assertIn('Ready', html)
        self.assertIn('bg-sky-500/15', html)
        self.assertIn('bg-amber-500/15', html)
        self.assertIn('bg-emerald-500/15', html)

