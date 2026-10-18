from django.core.management.base import BaseCommand
from apps.sales.models import Customer, SalesOrder, Product
from django.db.models import Count


class Command(BaseCommand):
    help = 'Cleans up duplicate customers and duplicate sales orders from the database'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Checking for duplicate customer records..."))
        
        # 1. Clean up duplicate customer accounts with 0 orders
        deleted_customers = 0
        all_names = set(Customer.objects.values_list('name', flat=True))
        for name in all_names:
            matches = list(Customer.objects.filter(name__iexact=name).order_by('id'))
            if len(matches) > 1:
                # Keep the one that has orders, or the earliest one
                with_orders = [c for c in matches if c.orders.exists()]
                if with_orders:
                    keep = with_orders[0]
                else:
                    keep = matches[0]
                
                for c in matches:
                    if c.id != keep.id and not c.orders.exists():
                        self.stdout.write(f"Deleting unused duplicate customer {c.id} ('{c.name}')")
                        c.delete()
                        deleted_customers += 1

        self.stdout.write(self.style.SUCCESS(f"Cleaned up {deleted_customers} duplicate customer profiles."))

        # 2. Check for duplicate SalesOrder records (exact same customer, product, date, qty, amount created within 60 seconds)
        self.stdout.write(self.style.NOTICE("Checking for duplicate sales orders..."))
        deleted_orders = 0
        seen_order_ids = set()
        
        all_orders = list(SalesOrder.all_objects.select_related('customer', 'product').order_by('id'))
        for i, o1 in enumerate(all_orders):
            if o1.id in seen_order_ids:
                continue
            for o2 in all_orders[i+1:]:
                if o2.id in seen_order_ids:
                    continue
                if o1.customer_id == o2.customer_id and o1.product_id == o2.product_id:
                    if o1.order_date == o2.order_date and o1.quantity_kg == o2.quantity_kg and o1.total_amount == o2.total_amount:
                        time_diff = abs((o1.created_at - o2.created_at).total_seconds()) if (o1.created_at and o2.created_at) else 9999
                        if time_diff <= 120 and o1.order_number == o2.order_number:
                            self.stdout.write(f"Found exact duplicate order {o2.id} ({o2.order_number}) of order {o1.id}. Removing...")
                            seen_order_ids.add(o2.id)
                            o2.delete()
                            deleted_orders += 1

        self.stdout.write(self.style.SUCCESS(f"Cleaned up {deleted_orders} duplicate sales order records."))
        self.stdout.write(self.style.SUCCESS("All sales data clean!"))
