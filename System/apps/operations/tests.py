from django.test import TestCase
from decimal import Decimal
from django.urls import reverse
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
        # Transfer 2 units (2 * 250 = 500 Crilings)
        response = self.client.post('/operations/pond/transfer/', {
            'source_pond_id': breeding_pond.id,
            'destination_pond_id': main_pond.id,
            'target_product': '2',
            'transfer_quantity': '2',
        })
        self.assertEqual(response.status_code, 302)

        breeding_pond.refresh_from_db()
        main_pond.refresh_from_db()

        self.assertEqual(breeding_pond.crilings_count, 4250)
        self.assertEqual(breeding_pond.capacity, 19)
        self.assertEqual(main_pond.capacity, 530)

        # Deduct Product 1: Product 2 must NOT be deducted
        breeding_pond.deduct_stock(5, product_name='Breeder Crayfish')
        breeding_pond.refresh_from_db()
        self.assertEqual(breeding_pond.capacity, 14)
        self.assertEqual(breeding_pond.crilings_count, 4250)

    def test_deduct_product_1_does_not_deduct_product_2(self):
        """Verify that deducting Product 1 (Breeder Crayfish) does NOT deduct Product 2 (Crilings)."""
        bp = Pond.objects.create(
            farm=self.farm,
            name='BP-INDEP-TEST',
            location='Breeding Pond',
            size=Decimal('50.00'),
            depth=Decimal('1.00'),
            capacity=20,
            capacity_2=5000,
            product_name='Breeder Crayfish',
            product_name_2='Crilings',
            status=Pond.Status.ACTIVE
        )
        self.assertEqual(bp.capacity, 20)
        self.assertEqual(bp.crilings_count, 5000)

        # Deduct 1 breeder via deduct_stock (Product 1)
        bp.deduct_stock(1, product_name='Breeder Crayfish')
        bp.refresh_from_db()
        self.assertEqual(bp.capacity, 19)
        self.assertEqual(bp.crilings_count, 5000)

        # Deduct 6 more breeders (down to 13)
        bp.deduct_stock(6, product_name='Breeder Crayfish')
        bp.refresh_from_db()
        self.assertEqual(bp.capacity, 13)
        self.assertEqual(bp.crilings_count, 5000)

        # Edit pond via client POST
        self.client.login(username='pondowner', password='password123')
        from apps.sales.models import Product
        Product.objects.get_or_create(name='Breeder Crayfish', defaults={'unit_price': 100})
        Product.objects.get_or_create(name='Crilings', defaults={'unit_price': 10})
        resp = self.client.post(f'/operations/pond/{bp.id}/edit/', {
            'name': 'BP-INDEP-TEST',
            'category': 'Breeding Pond',
            'product_name': 'Breeder Crayfish',
            'capacity': 10,
            'product_name_2': 'Crilings',
            'capacity_2': 5000,
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        bp.refresh_from_db()
        self.assertEqual(bp.capacity, 10)
        self.assertEqual(bp.crilings_count, 5000)


    def test_main_pond_2000_capacity_limit_on_model(self):
        from django.core.exceptions import ValidationError
        # Creating with <= 2000 works
        pond = Pond.objects.create(
            farm=self.farm,
            name='MAIN-LIMIT-OK',
            location='Main Pond',
            size=Decimal('100.00'),
            depth=Decimal('1.50'),
            capacity=2000,
            status=Pond.Status.ACTIVE
        )
        self.assertEqual(pond.capacity, 2000)

        # Calling clean with > 2000 raises ValidationError
        pond.capacity = 2001
        with self.assertRaises(ValidationError):
            pond.clean()

        # Calling save with > 2000 raises ValueError
        with self.assertRaises(ValueError):
            pond.save()

    def test_main_pond_2000_capacity_limit_on_transfer(self):
        main_pond = Pond.objects.create(
            farm=self.farm,
            name='MAIN-CAP-TEST',
            location='Main Pond',
            size=Decimal('100.00'),
            depth=Decimal('1.50'),
            capacity=1750,
            product_name='Crayfish',
            status=Pond.Status.ACTIVE
        )
        breeding_pond = Pond.objects.create(
            farm=self.farm,
            name='BREED-CAP-TEST',
            location='Breeding Pond',
            size=Decimal('80.00'),
            depth=Decimal('1.20'),
            capacity=10,
            capacity_2=500,
            product_name='Breeder Crayfish',
            product_name_2='Crilings',
            status=Pond.Status.ACTIVE
        )
        self.client.login(username='pondowner', password='password123')

        # Attempt to transfer 2 units (2 * 250 = 500) into 1750 -> total 2250 > 2000 (must be blocked)
        response = self.client.post('/operations/pond/transfer/', {
            'source_pond_id': breeding_pond.id,
            'destination_pond_id': main_pond.id,
            'target_product': '2',
            'transfer_quantity': '2',
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        main_pond.refresh_from_db()
        breeding_pond.refresh_from_db()

        # Verify quantities did NOT change
        self.assertEqual(main_pond.capacity, 1750)
        self.assertEqual(breeding_pond.crilings_count, 500)

        # Now transfer 1 unit (1 * 250 = 250) into 1750 -> total 2000 == 2000 (must succeed)
        response_ok = self.client.post('/operations/pond/transfer/', {
            'source_pond_id': breeding_pond.id,
            'destination_pond_id': main_pond.id,
            'target_product': '2',
            'transfer_quantity': '1',
        }, follow=True)

        self.assertEqual(response_ok.status_code, 200)
        main_pond.refresh_from_db()
        breeding_pond.refresh_from_db()

        self.assertEqual(main_pond.capacity, 2000)
        self.assertEqual(breeding_pond.crilings_count, 250)

    def test_breeding_pond_crilings_harvest_multiplier(self):
        """Verify harvesting 1 unit of Product 2 (Crilings) credits 250 pcs to sales product inventory."""
        from apps.sales.models import Product
        sale_prod, _ = Product.objects.get_or_create(
            name='Crilings',
            defaults={'unit_price': Decimal('5.00'), 'quantity_kg': Decimal('0')}
        )
        initial_stock = sale_prod.quantity_kg or Decimal('0')

        bp = Pond.objects.create(
            farm=self.farm,
            name='BREED-HARV-TEST',
            location='Breeding Pond',
            size=Decimal('100.00'),
            depth=Decimal('1.20'),
            capacity=10,
            capacity_2=1000,
            product_name='Breeder Crayfish',
            product_name_2='Crilings',
            status=Pond.Status.ACTIVE
        )
        self.client.login(username='pondowner', password='password123')

        # Harvest 2 units of Product 2 -> credits 2 * 250 = 500 pcs to inventory
        response = self.client.post(f'/harvest/pond/{bp.id}/harvest/', {
            'target_product': '2',
            'destination_product_id': sale_prod.id,
            'harvest_quantity': '2',
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        bp.refresh_from_db()
        sale_prod.refresh_from_db()

        self.assertEqual(bp.crilings_count, 500)
        self.assertEqual(sale_prod.quantity_kg, initial_stock + Decimal('500'))

    def test_main_pond_2000_capacity_limit_on_form(self):
        from apps.operations.template_views import PondForm
        from apps.sales.models import Product
        Product.objects.get_or_create(name='Crayfish', defaults={'unit_price': 100})

        # Main Pond with 2001 capacity should fail form validation
        form_invalid = PondForm(data={
            'name': 'MAIN-FORM-FAIL',
            'category': 'Main Pond',
            'product_name': 'Crayfish',
            'capacity': 2001,
        }, user=self.owner)
        self.assertFalse(form_invalid.is_valid())
        self.assertIn('capacity', form_invalid.errors)

        # Main Pond with 2000 capacity should be valid
        form_valid = PondForm(data={
            'name': 'MAIN-FORM-OK',
            'category': 'Main Pond',
            'product_name': 'Crayfish',
            'capacity': 2000,
        }, user=self.owner)
        self.assertTrue(form_valid.is_valid())

    def test_mortality_daily_reset_and_status(self):
        """Test that past mortality records (e.g. 3 days ago) do not show as recorded today."""
        from django.utils import timezone
        from django.db.models import Q
        import datetime
        from apps.operations.models import PondMortalityLog

        pond = Pond.objects.create(
            farm=self.farm,
            name='BREEDING-MORT-RESET',
            size=Decimal('100.00'),
            depth=Decimal('1.50'),
            location='Breeding Pond',
            capacity=20,
            status=Pond.Status.ACTIVE
        )

        three_days_ago = timezone.now() - datetime.timedelta(days=3)
        past_date = three_days_ago.date()

        log = PondMortalityLog.objects.create(
            pond=pond,
            product_name='Breeder Crayfish',
            quantity=4,
            reason='thirsty',
            date=past_date
        )
        PondMortalityLog.objects.filter(id=log.id).update(recorded_at=three_days_ago, date=past_date)

        today = timezone.localdate()
        today_match = PondMortalityLog.objects.filter(pond=pond).filter(
            Q(date=today) | Q(recorded_at__date=today)
        ).first()

        self.assertIsNone(today_match)

    def test_record_and_reset_mortality_view(self):
        """Test record_mortality view deducts stock and reset_mortality view restores it."""
        import json
        from django.test import RequestFactory
        from apps.operations.template_views import record_mortality, reset_mortality
        from apps.operations.models import PondMortalityLog

        pond = Pond.objects.create(
            farm=self.farm,
            name='BREEDING-MORT-TEST',
            size=Decimal('100.00'),
            depth=Decimal('1.50'),
            location='Breeding Pond',
            capacity=20,
            status=Pond.Status.ACTIVE
        )

        rf = RequestFactory()
        
        # 1. Record mortality
        payload = {
            'logs': [
                {
                    'pond_id': pond.id,
                    'product_name': 'Breeder Crayfish',
                    'quantity': 5,
                    'reason': 'water quality'
                }
            ]
        }
        req = rf.post('/operations/record-mortality/', data=json.dumps(payload), content_type='application/json')
        req.user = self.owner
        resp = record_mortality(req)
        self.assertEqual(resp.status_code, 200)

        pond.refresh_from_db()
        self.assertEqual(pond.capacity, 15)
        self.assertTrue(PondMortalityLog.objects.filter(pond=pond).exists())

        # 2. Reset mortality
        reset_req = rf.post('/operations/reset-mortality/', data=json.dumps({'category': 'Breeding Pond'}), content_type='application/json')
        reset_req.user = self.owner
        reset_resp = reset_mortality(reset_req)
        self.assertEqual(reset_resp.status_code, 200)

        pond.refresh_from_db()
        self.assertEqual(pond.capacity, 20)
        self.assertFalse(PondMortalityLog.objects.filter(pond=pond).exists())

    def test_clear_today_mortality_management_command(self):
        """Test clear_today_mortality management command clears logs and restores stock."""
        from django.core.management import call_command
        from apps.operations.models import PondMortalityLog

        pond = Pond.objects.create(
            farm=self.farm,
            name='MAIN-MORT-CMD',
            size=Decimal('100.00'),
            depth=Decimal('1.50'),
            location='Main Pond',
            capacity=1000,
            status=Pond.Status.ACTIVE
        )

        pond.deduct_stock(25)
        self.assertEqual(pond.capacity, 975)

        PondMortalityLog.objects.create(
            pond=pond,
            product_name='Crayfish',
            quantity=25,
            reason='cannibalism'
        )

        call_command('clear_today_mortality')

        pond.refresh_from_db()
        self.assertEqual(pond.capacity, 1000)
        self.assertEqual(PondMortalityLog.objects.filter(pond=pond).count(), 0)
    def test_azula_growth_and_edit_quantity(self):
        """Test Azula ponds grow by +2 per day and editing resets baseline to current quantity."""
        from datetime import timedelta
        from django.utils import timezone
        from django.urls import reverse
        from apps.sales.models import Product
        today = timezone.localdate()

        Product.objects.create(name='Azula', unit_price=Decimal('10.00'), is_active=True)

        azula_pond = Pond.objects.create(
            farm=self.farm,
            name='AZULA-TEST-POND',
            size=Decimal('10.00'),
            depth=Decimal('1.00'),
            location='Azula',
            capacity=10,
            transfer_date=today - timedelta(days=5),
            status=Pond.Status.ACTIVE
        )

        # 5 days * 2 = 10 growth; 10 + 10 = 20
        self.assertEqual(azula_pond.current_azula_quantity, 20)

        # Edit form GET request pre-fills with current quantity (20)
        from apps.operations.template_views import PondForm
        form = PondForm(instance=azula_pond)
        self.assertEqual(form['capacity'].value(), 20)

        # Editing quantity to 50 updates baseline to today so current quantity is 50
        self.client.force_login(self.owner)
        response = self.client.post(reverse('ponds:pond_edit', args=[azula_pond.id]), {
            'name': 'AZULA-TEST-POND',
            'category': 'Azula',
            'product_name': 'Azula',
            'capacity': 50,
            'transfer_date': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
            'status': 'active'
        })
        self.assertEqual(response.status_code, 302)

        azula_pond.refresh_from_db()
        self.assertEqual(azula_pond.capacity, 50)
        self.assertEqual(azula_pond.transfer_date, today)
        self.assertEqual(azula_pond.current_azula_quantity, 50)

        # Test deduct_stock on Azula
        deducted = azula_pond.deduct_stock(10)
        self.assertEqual(deducted, 10)
        azula_pond.refresh_from_db()
        self.assertEqual(azula_pond.capacity, 40)
        self.assertEqual(azula_pond.current_azula_quantity, 40)


class YieldSubpageRoutingTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='yieldowner', email='yieldowner@lantad.com', password='password123', role='owner')
        self.client.force_login(self.owner)

    def test_yield_subpage_render_and_routing(self):
        # 1. Bare /operations/ redirects to ?type=yield
        resp_bare = self.client.get(reverse('ponds:list'))
        self.assertEqual(resp_bare.status_code, 302)
        self.assertIn('?type=yield', resp_bare.url)

        # 2. ?type=yield loads yield.html
        resp_yield = self.client.get(reverse('ponds:list') + '?type=yield')
        self.assertEqual(resp_yield.status_code, 200)
        self.assertTemplateUsed(resp_yield, 'operations/yield.html')
        self.assertContains(resp_yield, 'Products for Harvest')

        # 3. Dedicated /operations/yield/ loads yield.html
        resp_named = self.client.get(reverse('ponds:yield'))
        self.assertEqual(resp_named.status_code, 200)
        self.assertTemplateUsed(resp_named, 'operations/yield.html')

        # 4. ?type=pond loads operations/list.html
        resp_pond = self.client.get(reverse('ponds:list') + '?type=pond')
        self.assertEqual(resp_pond.status_code, 200)
        self.assertTemplateUsed(resp_pond, 'operations/list.html')


class PondMortalityDashboardTest(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='mortdashowner', email='mortdash@lantad.com', password='password123', role='owner')
        self.farm = Farm.objects.create(name='Mort Farm', location='Silay', total_area=Decimal('1000.00'), owner=self.owner)
        self.pond = Pond.objects.create(
            farm=self.farm, name='Mortality Pond 1', size=Decimal('100.00'),
            depth=Decimal('1.5'), location='Main Pond', capacity=950, status=Pond.Status.ACTIVE
        )
        self.client.force_login(self.owner)

    def test_mortality_rate_properties_and_dashboard_tab(self):
        from django.utils import timezone
        from apps.operations.models import PondMortalityLog

        # Create 50 mortalities for Water Quality
        PondMortalityLog.objects.create(
            pond=self.pond,
            product_name='Crayfish',
            quantity=50,
            reason='Water Quality',
            date=timezone.localdate()
        )

        # 50 dead, 950 stock -> total = 1000 -> 5.0%
        self.assertEqual(self.pond.mortality_rate_7d, 5.0)
        self.assertEqual(self.pond.mortality_rate_30d, 5.0)

        # Dashboard rendering test
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Sales Activity')
        self.assertContains(resp, 'Pond Mortality')
        self.assertContains(resp, 'Water Quality')
        self.assertContains(resp, 'Mortality Pond 1')
        self.assertContains(resp, '5.0%')


