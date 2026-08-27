import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.harvest.models import HarvestSchedule
from apps.operations.models import Pond
from apps.stock.models import StockBatch

print("=== HarvestSchedule Count ===")
print(f"Total: {HarvestSchedule.objects.count()}")
print(f"SCHEDULED: {HarvestSchedule.objects.filter(status=HarvestSchedule.Status.SCHEDULED).count()}")
print(f"IN_PROGRESS: {HarvestSchedule.objects.filter(status=HarvestSchedule.Status.IN_PROGRESS).count()}")

print("\n=== Ponds ===")
print(f"Total: {Pond.objects.count()}")
for pond in Pond.objects.all()[:5]:
    print(f"  - {pond.name} (status: {pond.status})")

print("\n=== StockBatch ===")
print(f"Total active: {StockBatch.objects.filter(is_active=True).count()}")
