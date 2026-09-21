"""
Complete Data Seeder for Lantad Superworm & Crayfish
Populates all farm entities, stock batches, feeds, market products, sales orders, and ML forecasts.
"""
import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.accounts.models import User
from apps.operations.models import Farm, Pond
from apps.stock.models import Species, StockBatch
from apps.feed.models import FeedType, FeedingLog
from apps.harvest.models import HarvestSchedule, HarvestRecord
from apps.sales.models import Customer, Product, SalesOrder, Delivery, Rider
from apps.analytics.models import HarvestForecast, SalesForecast

def seed():
    print("🌱 Seeding Lantad Superworm & Crayfish Database...")

    # 1. Update Superuser to Owner
    admin_user = User.objects.filter(is_superuser=True).first()
    if admin_user:
        admin_user.role = User.Role.OWNER
        admin_user.save()
        print(f"✓ Updated superuser '{admin_user.username}' to Owner role.")

    # 2. Create Farm & Ponds
    farm, _ = Farm.objects.get_or_create(
        name="Silay Superworm & Crayfish Farm",
        defaults={
            'location': 'Silay Superworm & Crayfish, Lantad Silay City',
            'owner_name': 'Kymer Crisostomo',
            'phone': '09123456789',
            'total_area_sqm': Decimal('5000.00'),
        }
    )

    pond1, _ = Pond.objects.get_or_create(
        name="Pond 1 - Redclaw Growout",
        farm=farm,
        defaults={
            'water_type': Pond.WaterType.FRESHWATER,
            'length_m': Decimal('20.0'),
            'width_m': Decimal('10.0'),
            'depth_m': Decimal('1.5'),
            'volume_cubic_meters': Decimal('300.0'),
            'max_capacity': 2500,
            'status': Pond.Status.ACTIVE,
            'location': 'Sector A',
            'transfer_date': datetime.now().date() - timedelta(days=5),
        }
    )

    pond2, _ = Pond.objects.get_or_create(
        name="Pond 2 - Superworm Breeding Facility",
        farm=farm,
        defaults={
            'water_type': Pond.WaterType.FRESHWATER,
            'length_m': Decimal('15.0'),
            'width_m': Decimal('8.0'),
            'depth_m': Decimal('1.2'),
            'volume_cubic_meters': Decimal('144.0'),
            'max_capacity': 5000,
            'status': Pond.Status.ACTIVE,
            'location': 'Sector B',
            'transfer_date': datetime.now().date() - timedelta(days=10),
        }
    )

    azula_pond, _ = Pond.objects.get_or_create(
        name="Azula Sector 1",
        farm=farm,
        defaults={
            'water_type': Pond.WaterType.FRESHWATER,
            'length_m': Decimal('10.0'),
            'width_m': Decimal('5.0'),
            'depth_m': Decimal('1.0'),
            'volume_cubic_meters': Decimal('50.0'),
            'max_capacity': 1000,
            'status': Pond.Status.ACTIVE,
            'location': 'Azula Section',
            'transfer_date': datetime.now().date() - timedelta(days=12),
        }
    )

    # 3. Species
    crayfish_species, _ = Species.objects.get_or_create(
        name="Australian Redclaw Crayfish",
        defaults={
            'scientific_name': 'Cherax quadricarinatus',
            'category': Species.Category.SHRIMP,
            'optimal_temperature_min': Decimal('23.0'),
            'optimal_temperature_max': Decimal('31.0'),
            'optimal_ph_min': Decimal('6.5'),
            'optimal_ph_max': Decimal('8.5'),
            'days_to_harvest': 180,
            'target_harvest_weight': Decimal('100.0'),
            'expected_fcr': Decimal('1.6'),
            'expected_survival_rate': Decimal('85.0'),
        }
    )

    superworm_species, _ = Species.objects.get_or_create(
        name="Superworm (Zophobas morio)",
        defaults={
            'scientific_name': 'Zophobas morio',
            'category': Species.Category.OTHER,
            'optimal_temperature_min': Decimal('22.0'),
            'optimal_temperature_max': Decimal('28.0'),
            'optimal_ph_min': Decimal('6.0'),
            'optimal_ph_max': Decimal('8.0'),
            'days_to_harvest': 90,
            'target_harvest_weight': Decimal('1.5'),
            'expected_fcr': Decimal('2.0'),
            'expected_survival_rate': Decimal('92.0'),
        }
    )

    # 4. Stock Batches
    batch1, _ = StockBatch.objects.get_or_create(
        batch_number="BATCH-CRAY-2026-001",
        defaults={
            'pond': pond1,
            'species': crayfish_species,
            'stocking_date': datetime.now().date() - timedelta(days=120),
            'initial_quantity': 2000,
            'current_quantity': 1850,
            'initial_average_weight': Decimal('15.0'),
            'current_average_weight': Decimal('78.5'),
            'source': 'Lantad Hatchery',
            'status': StockBatch.Status.GROWING,
            'is_active': True,
        }
    )

    batch2, _ = StockBatch.objects.get_or_create(
        batch_number="BATCH-WORM-2026-002",
        defaults={
            'pond': pond2,
            'species': superworm_species,
            'stocking_date': datetime.now().date() - timedelta(days=45),
            'initial_quantity': 10000,
            'current_quantity': 9600,
            'initial_average_weight': Decimal('0.3'),
            'current_average_weight': Decimal('1.2'),
            'source': 'Silay Breeding Colony',
            'status': StockBatch.Status.GROWING,
            'is_active': True,
        }
    )

    # 5. Feeds & Feeding Logs
    feed1, _ = FeedType.objects.get_or_create(
        name="Premium Crayfish Sinking Pellets (38% Protein)",
        defaults={
            'category': FeedType.Category.COMMERCIAL,
            'price_per_kg': Decimal('85.00'),
            'protein_content': Decimal('38.0'),
            'description': 'High-protein aquatic formulation for rapid molt & exoskeleton development.',
            'accent_color': 'emerald',
            'is_active': True,
        }
    )

    feed2, _ = FeedType.objects.get_or_create(
        name="Organic Wheat Bran & Vegetable Substrate",
        defaults={
            'category': FeedType.Category.ORGANIC,
            'price_per_kg': Decimal('45.00'),
            'protein_content': Decimal('18.0'),
            'description': 'Sterilized dietary base with carrot/potato hydration slices for superworms.',
            'accent_color': 'amber',
            'is_active': True,
        }
    )

    FeedingLog.objects.get_or_create(
        stock_batch=batch1,
        feed_type=feed1,
        feeding_time=datetime.now() - timedelta(hours=3),
        defaults={
            'quantity_kg': Decimal('4.5'),
            'mortality_count': 0,
            'water_temperature': Decimal('27.5'),
            'ph_level': Decimal('7.4'),
            'dissolved_oxygen': Decimal('6.8'),
            'notes': 'Optimal feeding activity observed.',
        }
    )

    # 6. Market Products
    p1, _ = Product.objects.get_or_create(
        name="Australian Redclaw Crayfish (Live Large)",
        defaults={
            'species': crayfish_species,
            'pond': pond1,
            'category': Product.Category.SHRIMP,
            'unit_type': Product.UnitType.KG,
            'price_per_kg': Decimal('850.00'),
            'quantity_kg': Decimal('65.0'),
            'reorder_level_kg': Decimal('20.0'),
            'description': 'Freshly harvested large live Australian Redclaw (75g - 100g+ per piece).',
            'is_active': True,
        }
    )

    p2, _ = Product.objects.get_or_create(
        name="Australian Redclaw Crayfish (Medium Plate Size)",
        defaults={
            'species': crayfish_species,
            'pond': pond1,
            'category': Product.Category.SHRIMP,
            'unit_type': Product.UnitType.KG,
            'price_per_kg': Decimal('650.00'),
            'quantity_kg': Decimal('90.0'),
            'reorder_level_kg': Decimal('25.0'),
            'description': 'Sweet, tender succulent live crayfish ideal for restaurants and boil platters.',
            'is_active': True,
        }
    )

    p3, _ = Product.objects.get_or_create(
        name="Live Superworms (High Protein)",
        defaults={
            'species': superworm_species,
            'pond': pond2,
            'category': Product.Category.FISH,
            'unit_type': Product.UnitType.TUB,
            'price_per_kg': Decimal('150.00'),
            'quantity_kg': Decimal('150.0'),
            'reorder_level_kg': Decimal('30.0'),
            'description': 'Clean, gut-loaded live superworms for bird, reptile, and exotic pet nutrition.',
            'is_active': True,
        }
    )

    p4, _ = Product.objects.get_or_create(
        name="Breeder Redclaw Pair (1 Male + 1 Female)",
        defaults={
            'species': crayfish_species,
            'pond': pond1,
            'category': Product.Category.SHRIMP,
            'unit_type': Product.UnitType.PAIR,
            'price_per_kg': Decimal('450.00'),
            'quantity_kg': Decimal('35.0'),
            'reorder_level_kg': Decimal('10.0'),
            'description': 'High-fertility selected broodstock pair with red claw markings.',
            'is_active': True,
        }
    )

    # 7. Customers & Riders
    customer1, _ = Customer.objects.get_or_create(
        name="Bacolod Seafood Grill & Resto",
        defaults={
            'customer_type': Customer.Type.RESTAURANT,
            'contact_person': 'Chef Ronald M.',
            'phone': '09171234567',
            'email': 'orders@bacolodgrill.ph',
            'address': 'Lacson Street, Bacolod City',
        }
    )

    customer2, _ = Customer.objects.get_or_create(
        name="Silay Organic Market Buyers",
        defaults={
            'customer_type': Customer.Type.RETAILER,
            'contact_person': 'Maria Santos',
            'phone': '09289876543',
            'email': 'santos.market@gmail.com',
            'address': 'Public Plaza, Silay City',
        }
    )

    rider_user, _ = User.objects.get_or_create(
        username="rider_silay",
        defaults={
            'first_name': 'Marco',
            'last_name': 'Rider',
            'role': User.Role.RIDER,
            'is_active': True,
        }
    )

    rider, _ = Rider.objects.get_or_create(
        user=rider_user,
        defaults={
            'name': 'Marco Rider',
            'phone': '09301112233',
            'vehicle_type': 'Motorcycle with Insulated Box',
            'status': Rider.Status.AVAILABLE,
        }
    )

    # 8. Sales Orders & Delivery History
    now = datetime.now()
    order_dates = [
        now.date(),
        now.date() - timedelta(days=1),
        now.date() - timedelta(days=2),
        now.date() - timedelta(days=3),
        now.date() - timedelta(days=5),
        now.date() - timedelta(days=7),
    ]

    for i, o_date in enumerate(order_dates):
        order_num = f"ORD-2026-{1000 + i}"
        status = SalesOrder.Status.COMPLETED if i > 1 else (SalesOrder.Status.IN_TRANSIT if i == 1 else SalesOrder.Status.PENDING)
        prod = p1 if i % 2 == 0 else p3
        qty = Decimal(str(3 + (i * 2)))
        total = qty * prod.price_per_kg
        
        order, created = SalesOrder.objects.get_or_create(
            order_number=order_num,
            defaults={
                'customer': customer1 if i % 2 == 0 else customer2,
                'product': prod,
                'quantity_kg': qty,
                'unit_price': prod.price_per_kg,
                'total_amount': total,
                'order_date': o_date,
                'status': status,
                'payment_status': SalesOrder.PaymentStatus.PAID if status == SalesOrder.Status.COMPLETED else SalesOrder.PaymentStatus.PENDING,
                'payment_method': 'cash',
                'delivery_address': 'Silay City Central Logistics Point',
            }
        )

        if created:
            Delivery.objects.create(
                order=order,
                rider=rider if status != SalesOrder.Status.PENDING else None,
                delivery_location=order.delivery_address,
                quantity_kg=order.quantity_kg,
                status=Delivery.Status.DELIVERED if status == SalesOrder.Status.COMPLETED else (Delivery.Status.IN_TRANSIT if status == SalesOrder.Status.IN_TRANSIT else Delivery.Status.SCHEDULED),
                scheduled_date=o_date,
                delivered_date=o_date if status == SalesOrder.Status.COMPLETED else None,
            )

    # 9. Harvest Schedules & Forecasts
    sched, _ = HarvestSchedule.objects.get_or_create(
        stock_batch=batch1,
        scheduled_date=now.date() + timedelta(days=14),
        defaults={
            'target_weight_kg': Decimal('150.0'),
            'target_count': 1500,
            'status': HarvestSchedule.Status.SCHEDULED,
            'notes': 'Scheduled for Bacolod restaurant advance reservation.',
        }
    )

    HarvestForecast.objects.get_or_create(
        stock_batch=batch1,
        predicted_harvest_date=now.date() + timedelta(days=14),
        defaults={
            'predicted_biomass_kg': Decimal('165.5'),
            'predicted_avg_weight_g': Decimal('88.0'),
            'confidence_level': Decimal('92.5'),
        }
    )

    print("✅ All sample data successfully seeded!")

if __name__ == '__main__':
    seed()
