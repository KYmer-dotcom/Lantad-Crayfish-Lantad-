import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from apps.operations.models import PondMortalityLog, Pond


class Command(BaseCommand):
    help = "Clear recorded pond mortality logs for today (or all) and restore deducted pond stock."

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clear all mortality logs across all dates and restore pond stock.',
        )
        parser.add_argument(
            '--date',
            type=str,
            default=None,
            help='Clear mortality logs for a specific date (YYYY-MM-DD). Defaults to today.',
        )

    def handle(self, *args, **options):
        is_all = options.get('all')
        specific_date_str = options.get('date')

        if is_all:
            logs = PondMortalityLog.objects.all()
            target_label = "all dates"
        elif specific_date_str:
            target_date = datetime.date.fromisoformat(specific_date_str)
            logs = PondMortalityLog.objects.filter(
                Q(date=target_date) | Q(recorded_at__date=target_date)
            )
            target_label = str(target_date)
        else:
            today = timezone.localdate()
            utc_today = timezone.now().date()
            logs = PondMortalityLog.objects.filter(
                Q(date=today) | Q(recorded_at__date=today) |
                Q(date=utc_today) | Q(recorded_at__date=utc_today)
            )
            target_label = f"today ({today})"

        count = logs.count()
        if count == 0:
            self.stdout.write(self.style.WARNING(f"No mortality logs found for {target_label}."))
            return

        for log in logs:
            pond = log.pond
            qty = log.quantity or 0
            if qty > 0:
                prod = (log.product_name or '').lower()
                if pond.location == 'Main Pond' and pond.transfer_batches.exists():
                    last_batch = pond.transfer_batches.order_by('-transfer_date', '-id').first()
                    if last_batch:
                        last_batch.quantity += qty
                        last_batch.save(update_fields=['quantity'])
                        pond.capacity = sum(b.quantity for b in pond.transfer_batches.all())
                    else:
                        pond.capacity = (pond.capacity or 0) + qty
                elif pond.location == 'Breeding Pond' and 'criling' in prod:
                    pond.capacity_2 = (pond.capacity_2 or 0) + qty
                else:
                    pond.capacity = (pond.capacity or 0) + qty

                pond.status = Pond.Status.ACTIVE
                pond.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Restored {qty} {log.product_name} to {pond.name} (Now capacity: {pond.capacity}, capacity_2: {pond.capacity_2})"
                    )
                )

        deleted_count, _ = logs.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleared {count} mortality log(s) for {target_label} and restored pond stock."
            )
        )
