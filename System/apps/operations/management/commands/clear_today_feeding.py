from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.operations.models import PondFeedingLog
from apps.feed.models import FeedStockMovement, FeedType


class Command(BaseCommand):
    help = "Clear all recorded pond feeding logs and movements for today so you can test freshly."

    def handle(self, *args, **options):
        today = timezone.localdate()
        
        # 1. Reverse today's feed stock movements
        movements = FeedStockMovement.objects.filter(moved_at__date=today, movement_type=FeedStockMovement.MovementType.OUT)
        for mov in movements:
            feed = mov.feed_type
            if feed and feed.kg_per_sack and feed.kg_per_sack > 0:
                # delta_kg is negative (e.g. -0.50), so abs(delta_kg) is what was deducted
                deducted_kg = abs(mov.delta_kg)
                curr_kg = (feed.quantity_sacks or 0) * feed.kg_per_sack
                feed.quantity_sacks = (curr_kg + deducted_kg) / feed.kg_per_sack
                feed.save(update_fields=['quantity_sacks'])
                self.stdout.write(self.style.SUCCESS(f"Restored {deducted_kg}kg to {feed.name}"))
        
        deleted_movements, _ = movements.delete()
        
        # 2. Delete today's feeding logs
        logs = PondFeedingLog.objects.filter(recorded_at__date=today)
        logs_count = logs.count()
        logs.delete()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully cleared {logs_count} feeding logs and restored inventory for {today}."
        ))
