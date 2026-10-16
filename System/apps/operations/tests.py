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
        today = timezone.localdate()
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
        self.assertFalse(pond.is_sanitization_due)
        self.assertEqual(pond.sanitization_days_remaining, 15)

        # Trying to sanitize before 15 days is blocked
        response_blocked = self.client.post(f'/operations/pond/{pond.id}/sanitize/')
        self.assertEqual(response_blocked.status_code, 302)

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
        self.assertFalse(pond.is_sanitization_due)

        # Subsequent bulk sanitize attempt while up-to-date is blocked
        response2 = self.client.post(
            '/operations/operations/azula-sanitize/',
            data=json.dumps({'pond_ids': [pond.id]}),
            content_type='application/json'
        )
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.json().get('status'), 'error')

    def test_breeding_pond_crilings_transfer_deduction(self):
        """Verify transferring Crilings from Breeding Pond deducts accurately."""
        breeding_pond = Pond.objects.create(
            farm=self.farm,
            name='BREEDING-01',
            location='Breeding Pond',
            size=Decimal('50.00'),
            depth=Decimal('1.00'),
            capacity=19,
            product_name='Breeder Crayfish',
            product_name_2='Crilings',
            status=Pond.Status.ACTIVE
        )
        main_pond = Pond.objects.create(
            farm=self.farm,
            name='MAIN-01',
            location='Main Pond',
            size=Decimal('100.00'),
            depth=Decimal('1.50'),
            capacity=30,
            product_name='Crayfish',
            status=Pond.Status.ACTIVE
        )

        self.assertEqual(breeding_pond.crilings_count, 4750)
        self.assertEqual(breeding_pond.capacity, 19)

        self.client.login(username='pondowner', password='password123')
        response = self.client.post('/operations/pond/transfer/', {
            'source_pond_id': breeding_pond.id,
            'destination_pond_id': main_pond.id,
            'target_product': '2',
            'transfer_quantity': '120',
        })
        self.assertEqual(response.status_code, 302)

        breeding_pond.refresh_from_db()
        main_pond.refresh_from_db()

        self.assertEqual(breeding_pond.crilings_count, 4630)
        self.assertEqual(breeding_pond.capacity, 19)
        self.assertEqual(main_pond.capacity, 150)




