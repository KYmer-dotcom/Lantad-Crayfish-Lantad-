from django.test import TestCase
from decimal import Decimal
from django.contrib.auth import get_user_model
from apps.operations.models import Farm, Pond
from apps.stock.models import Species

User = get_user_model()

class FarmFacilityTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='farmowner', email='owner@lantad.com', password='password123', role='owner')

    def test_farm_creation(self):
        farm = Farm.objects.create(
            name='Silay Aquaculture Complex',
            location='Brgy. Lantad, Silay City',
            total_area=Decimal('5000.00'),
            owner=self.owner
        )
        self.assertEqual(farm.name, 'Silay Aquaculture Complex')
        self.assertEqual(farm.active_ponds, 0)
        self.assertEqual(farm.total_ponds, 0)

class PondOperationalTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='pondowner', email='pondowner@lantad.com', password='password123', role='owner')
        self.farm = Farm.objects.create(name='Main AquaFarm', location='Silay City', total_area=Decimal('10000.00'), owner=self.owner)
        self.species = Species.objects.create(name='Red Claw Crayfish', category=Species.Category.CRUSTACEANS)

    def test_pond_creation_and_capacity(self):
        pond = Pond.objects.create(
            farm=self.farm,
            name='POND-01',
            size=Decimal('150.00'),
            depth=Decimal('1.50'),
            capacity=2000,
            status=Pond.Status.ACTIVE
        )
        self.assertEqual(pond.name, 'POND-01')
        self.assertEqual(pond.capacity, 2000)
        self.assertEqual(pond.status, Pond.Status.ACTIVE)

    def test_pond_status_transition_to_maintenance(self):
        pond = Pond.objects.create(
            farm=self.farm,
            name='POND-02',
            size=Decimal('120.00'),
            depth=Decimal('1.20'),
            capacity=1500,
            status=Pond.Status.ACTIVE
        )
        pond.status = Pond.Status.MAINTENANCE
        pond.save()
        pond.refresh_from_db()
        self.assertEqual(pond.status, Pond.Status.MAINTENANCE)
