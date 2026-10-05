from django.core.management.base import BaseCommand
import datetime
from apps.operations.models import Pond, PondTransferBatch
from apps.sales.models import Product


class Command(BaseCommand):
    help = 'Restores POND 1 (Main Pond) and resets sale products inventory to 0'

    def handle(self, *args, **options):
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
            self.stdout.write(self.style.SUCCESS(f"Pond 1 in Main Pond restored with capacity {p.capacity} and 2 batches (34, 15)."))

        for prod in Product.objects.filter(is_active=True):
            prod.quantity_kg = 0
            prod.save(update_fields=['quantity_kg'])
        self.stdout.write(self.style.SUCCESS("All active products for sale reset to 0 Quantity."))
