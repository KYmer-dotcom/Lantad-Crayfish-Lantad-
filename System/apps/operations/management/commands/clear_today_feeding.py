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
            deducted_kg = abs(mov.delta_kg)
            curr_kg = (feed.quantity_sacks or 0) * feed.kg_per_sack
            new_sacks = (curr_kg + deducted_kg) / feed.kg_per_sack
            rounded = round(float(new_sacks))
            if float(new_sacks) > rounded and (float(new_sacks) - rounded) < 0.001:
                new_sacks = rounded
            feed.quantity_sacks = new_sacks
            feed.save(update_fields=['quantity_sacks'])
            self.stdout.write(self.style.SUCCESS(f"Restored {deducted_kg}kg to {feed.name} (Now {feed.quantity_sacks} sacks)"))
        
        deleted_movements, _ = movements.delete()
        
        # 2. Snap any existing feed types with fractional overshoots above full capacity (e.g. 3.0002 -> 3)
        for feed in FeedType.objects.all():
            curr_sacks = float(feed.quantity_sacks or 0)
            rounded = round(curr_sacks)
            if curr_sacks > rounded and (curr_sacks - rounded) < 0.001:
                feed.quantity_sacks = rounded
                feed.save(update_fields=['quantity_sacks'])
        
        # 3. Delete today's feeding logs
        logs = PondFeedingLog.objects.filter(recorded_at__date=today)
        logs_count = logs.count()
        logs.delete()

        self.stdout.write(self.style.SUCCESS(
            f"Successfully cleared {logs_count} feeding logs and restored inventory for {today}."
        ))
