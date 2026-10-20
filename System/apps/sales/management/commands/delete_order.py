from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.sales.models import Customer, SalesOrder


class Command(BaseCommand):
    help = 'Completely deletes a sales order and its customer from the database by order number or customer name'

    def add_arguments(self, parser):
        parser.add_argument('--order', type=str, help='Order number or partial order number (e.g. SO-20261018-0003 or 20261018-0003)')
        parser.add_argument('--customer', type=str, help='Customer name or partial name (e.g. Samuel Sian)')

    def handle(self, *args, **options):
        order_query = options.get('order')
        customer_query = options.get('customer')

        if not order_query and not customer_query:
            self.stdout.write(self.style.ERROR("Please specify --order or --customer."))
            return

        order_filter = Q()
        if order_query:
            clean_q = order_query.replace('#', '').strip()
            order_filter |= Q(order_number__icontains=clean_q)
        if customer_query:
            order_filter |= Q(customer__name__icontains=customer_query.strip())

        orders = list(SalesOrder.all_objects.filter(order_filter).select_related('customer'))

        if not orders:
            self.stdout.write(self.style.WARNING(f"No orders found matching: order='{order_query}', customer='{customer_query}'"))
        else:
            self.stdout.write(self.style.NOTICE(f"Found {len(orders)} matching order(s):"))
            customer_candidates = set()
            for o in orders:
                cust_name = o.customer.name if o.customer else 'Guest'
                self.stdout.write(f"  - Order #{o.order_number}: {cust_name} | PHP {o.total_amount:,.2f} ({o.order_date})")
                if o.customer:
                    customer_candidates.add(o.customer)

            # Hard delete matching orders
            order_ids = [o.id for o in orders]
            qs = SalesOrder.all_objects.filter(id__in=order_ids)
            if hasattr(qs, 'hard_delete'):
                del_res = qs.hard_delete()
            else:
                del_res = qs.delete()
            deleted_count = del_res[0] if isinstance(del_res, (tuple, list)) else del_res
            self.stdout.write(self.style.SUCCESS(f"Successfully deleted {deleted_count} order record(s)."))

            # Clean up customers if they have no remaining orders
            for cust in customer_candidates:
                remaining_orders = cust.orders.count()
                if remaining_orders == 0:
                    cust_name = cust.name
                    linked_user = cust.user
                    cust.delete()
                    if linked_user:
                        linked_user.delete()
                    self.stdout.write(self.style.SUCCESS(f"Successfully deleted customer '{cust_name}' (0 orders remaining)."))
                else:
                    self.stdout.write(self.style.NOTICE(f"Customer '{cust.name}' retained ({remaining_orders} other order(s) remain)."))

        # Also check if explicit customer name was given without orders
        if customer_query:
            matching_custs = Customer.objects.filter(name__icontains=customer_query.strip())
            for c in matching_custs:
                if c.orders.count() == 0:
                    c_name = c.name
                    linked_u = c.user
                    c.delete()
                    if linked_u:
                        linked_u.delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted customer profile '{c_name}'."))
