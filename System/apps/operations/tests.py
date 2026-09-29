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

    def test_azula_sanitization_lifecycle(self):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()
        pond = Pond.objects.create(
            farm=self.farm,
            name='AZULA-POND-01',
            location='Azula',
            size=Decimal('50.00'),
            depth=Decimal('1.00'),
            capacity=1000,
            transfer_date=today - timedelta(days=20),
            status=Pond.Status.MAINTENANCE
        )
        # Next sanitization initially based on transfer_date
        self.assertEqual(pond.next_sanitization_date, pond.transfer_date + timedelta(days=15))

        # Client posts to sanitize view
        self.client.login(username='pondowner', password='password123')
        response = self.client.post(f'/operations/pond/{pond.id}/sanitize/')
        self.assertEqual(response.status_code, 302)
        
        pond.refresh_from_db()
        self.assertEqual(pond.last_sanitized_date, today)
        self.assertEqual(pond.next_sanitization_date, today + timedelta(days=15))
        self.assertEqual(pond.status, Pond.Status.ACTIVE)

    def test_record_azula_sanitization_bulk_api(self):
        import json
        from django.utils import timezone
        today = timezone.now().date()
        pond = Pond.objects.create(
            farm=self.farm,
            name='AZULA-POND-02',
            location='Azula',
            size=Decimal('50.00'),
            depth=Decimal('1.00'),
            capacity=1000,
            status=Pond.Status.ACTIVE
        )
        self.client.login(username='pondowner', password='password123')
        response = self.client.post(
            '/operations/operations/azula-sanitize/',
            data=json.dumps({'pond_ids': [pond.id]}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data.get('status'), 'success')
        self.assertEqual(data.get('sanitized_count'), 1)
        
        pond.refresh_from_db()
        self.assertEqual(pond.last_sanitized_date, today)


