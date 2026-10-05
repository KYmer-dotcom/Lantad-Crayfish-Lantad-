import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.operations.models import Pond, PondTransferBatch
from apps.sales.models import Product

p = Pond.objects.filter(name='POND 1', location='Main Pond').first()
if p:
    p.capacity = 49
    p.product_name = 'Crayfish'
    p.status = 'active'
    p.transfer_date = datetime.date(2026, 10, 6)
    p.save()
    p.transfer_batches.all().delete()
    PondTransferBatch.objects.create(pond=p, quantity=34, transfer_date=datetime.date(2026, 10, 6))
    PondTransferBatch.objects.create(pond=p, quantity=15, transfer_date=datetime.date(2026, 10, 6))
    print(f"Pond 1 in Main Pond restored with capacity {p.capacity} and {p.transfer_batches.count()} transfer batches.")

prod = Product.objects.filter(name='Crayfish', is_active=True).first()
if prod:
    prod.quantity_kg = 0
    prod.save()
    print("Crayfish for-sale inventory restored to 0.")
