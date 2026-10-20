"""
Core views for dashboard and main pages
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from django.db.models import Sum, Count, F
from django import forms
from django.db.models.functions import TruncDate, TruncMonth
from datetime import datetime, timedelta
from decimal import Decimal
import json
from apps.accounts.access import filter_by_pond, is_customer, is_rider, get_accessible_farms, get_accessible_ponds
from apps.accounts.models import User
from apps.sales.models import Customer


def customer_login(request):
    """Dedicated login page for customer accounts using Phone and Name."""
    if request.user.is_authenticated:
        if is_customer(request.user):
            auth_logout(request)
        else:
            return redirect('dashboard')

    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        name = request.POST.get('name', '').strip()

        # Extract only digits to check length
        phone_digits = ''.join(c for c in phone if c.isdigit())

        if not phone or not name:
            messages.error(request, 'All fields (Phone and Name) are required.')
        elif len(phone_digits) != 11:
            messages.error(request, 'Phone number must be exactly 11 digits.')
        else:
            # Check if user exists by phone or customer profile exists by phone
            user = User.objects.filter(username__iexact=phone).first()
            customer = Customer.objects.filter(phone__iexact=phone).first()
            
            # If both don't exist, this is a clean new registration!
            if not user and not customer:
                # Auto-register user with customer role
                user = User(
                    username=phone,
                    first_name=name,
                    role=User.Role.CUSTOMER,
                    is_active=True,
                )
                user.set_unusable_password()
                user.save()
                
                # Auto-create Customer profile
                Customer.objects.create(
                    user=user,
                    name=name,
                    phone=phone,
                    address="",
                    customer_type=Customer.Type.INDIVIDUAL,
                )
                auth_login(request, user)
                return redirect('sales:customer_portal')
            else:
                # Existing account found. Validate name matching!
                existing_customer = customer or Customer.objects.filter(user=user).first()
                if existing_customer and existing_customer.name.strip().lower() != name.strip().lower():
                    messages.error(request, 'This phone number is already registered under a different name.')
                else:
                    # If user is None (but customer profile existed), link it now!
                    if not user:
                        user = User(
                            username=phone,
                            first_name=name,
                            role=User.Role.CUSTOMER,
                            is_active=True,
                        )
                        user.set_unusable_password()
                        user.save()
                        existing_customer.user = user
                        existing_customer.save()
                    
                    auth_login(request, user)
                    return redirect('sales:customer_portal')

    return render(request, 'auth/customer_login.html')


def app_logout(request):
    """Role-aware logout redirect."""
    is_cust = False
    if request.user.is_authenticated:
        if not (request.user.is_superuser or request.user.is_staff or getattr(request.user, 'role', '') == 'owner' or getattr(request.user, 'is_owner', False)):
            if getattr(request.user, 'role', '') == 'customer' or getattr(request.user, 'is_customer', False):
                is_cust = True
    auth_logout(request)
    if is_cust:
        return redirect('sales:customer_portal')
    return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard view"""
    if is_customer(request.user):
        return redirect('sales:customer_portal')
    if is_rider(request.user):
        return redirect('sales:rider_portal')
    from apps.operations.models import Farm, Pond
    from apps.stock.models import StockBatch, Species
    from apps.feed.models import FeedingLog

    from apps.harvest.models import HarvestRecord, HarvestSchedule
    from apps.sales.models import SalesOrder
    from apps.analytics.models import HarvestForecast, SalesForecast
    
    from django.utils import timezone
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # Basic stats
    accessible_farms = get_accessible_farms(request.user)
    total_farms = accessible_farms.count()
    accessible_ponds = get_accessible_ponds(request.user)
    total_ponds = accessible_ponds.count()
    active_ponds = accessible_ponds.exclude(status=Pond.Status.EMPTY).count()
    if active_ponds == 0 and total_ponds > 0:
        active_ponds = total_ponds
    
    manager_info = None

    # Fish stats
    active_batches = filter_by_pond(request.user, StockBatch.objects.filter(is_active=True), 'pond')
    if active_batches.exists():
        total_fish = active_batches.aggregate(total=Sum('current_quantity'))['total'] or 0
        # Calculate total biomass (current_quantity * current_average_weight in kg)
        total_biomass = 0
        for batch in active_batches:
            if batch.current_quantity and batch.current_average_weight:
                total_biomass += (batch.current_quantity * float(batch.current_average_weight)) / 1000
    else:
        from apps.sales.models import Product
        active_products = Product.objects.filter(is_active=True)
        total_fish = active_products.filter(quantity_kg__gt=0).count()
        total_biomass = active_products.aggregate(total=Sum('quantity_kg'))['total'] or 0
    
    # 30-day stats
    feed_logs_30d = filter_by_pond(
        request.user,
        FeedingLog.objects.filter(feeding_time__date__gte=thirty_days_ago),
        'stock_batch__pond'
    )
    feed_used_30d = feed_logs_30d.aggregate(total=Sum('quantity_kg'))['total'] or 0
    feeding_count = feed_logs_30d.count()
    
    mortality_30d = 0
    mortality_events = 0
    
    harvest_30d_qs = filter_by_pond(
        request.user,
        HarvestRecord.objects.filter(harvest_date__gte=thirty_days_ago),
        'stock_batch__pond'
    )
    harvest_30d = harvest_30d_qs.aggregate(total=Sum('total_weight_kg'))['total'] or 0
    harvest_count = harvest_30d_qs.count()
    
    orders_30d = SalesOrder.objects.filter(order_date__gte=thirty_days_ago).exclude(status=SalesOrder.Status.CANCELLED)
    revenue_30d = orders_30d.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders_30d.count()
    daily_sales_qs = SalesOrder.objects.filter(order_date=today).exclude(status=SalesOrder.Status.CANCELLED)
    daily_sales_total = daily_sales_qs.aggregate(total=Sum('total_amount'))['total'] or 0
    pending_orders = SalesOrder.objects.filter(status__in=[SalesOrder.Status.PENDING, SalesOrder.Status.CONFIRMED, SalesOrder.Status.PROCESSING]).count()
    
    # Species distribution for pie chart
    species_data = []
    if active_batches.exists():
        species_counts = StockBatch.objects.filter(is_active=True).values('species__name').annotate(
            count=Sum('current_quantity')
        ).order_by('-count')[:10]
    else:
        from apps.sales.models import Product
        species_counts = Product.objects.filter(is_active=True).values('name').annotate(
            count=Sum('quantity_kg')
        ).order_by('-count')[:10]
    
    for item in species_counts:
        name = item.get('species__name') or item.get('name')
        count = item.get('count')
        if name and count:
            try:
                count_val = int(count) if isinstance(count, (int, float, str)) else 0
            except (ValueError, TypeError):
                count_val = int(float(count)) if count else 0
            species_data.append({
                'name': name,
                'count': count_val
            })

    farm_locations = [
        {
            'id': farm.id,
            'name': farm.name,
            'location': farm.location or 'Silay Superworm & Crayfish, Lantad Silay City',
            'pin_color': 'admin',
            'is_current_account': True
        }
        for farm in accessible_farms
        if farm.location or farm.name
    ]

    # Embedded analytics + reports sections for dashboard (Full Month Timeline)
    import calendar
    from datetime import date
    sales_qs = SalesOrder.objects.exclude(status=SalesOrder.Status.CANCELLED)
    latest_order = sales_qs.order_by('-order_date').first()
    ref_date = latest_order.order_date if latest_order else today
    
    current_year = ref_date.year
    current_month = ref_date.month
    _, num_days = calendar.monthrange(current_year, current_month)
    month_start = date(current_year, current_month, 1)
    month_end = date(current_year, current_month, num_days)
    month_name = month_start.strftime('%B %Y')
    
    monthly_sales = sales_qs.filter(order_date__gte=month_start, order_date__lte=month_end).aggregate(
        total_sales=Sum('total_amount'),
        total_qty=Sum('quantity_kg')
    )

    monthly_sales_records = sales_qs.filter(
        order_date__gte=month_start,
        order_date__lte=month_end
    ).annotate(day=TruncDate('order_date')).values('day').annotate(
        total_sales=Sum('total_amount'),
        total_qty=Sum('quantity_kg'),
        total_orders=Count('id')
    )
    
    sales_map = {item['day']: item for item in monthly_sales_records}
    
    # Generate all days for this month (e.g. Day 01 to Day 30)
    monthly_chart_labels = []
    monthly_chart_values = []
    for d in range(1, num_days + 1):
        day_date = date(current_year, current_month, d)
        monthly_chart_labels.append(day_date.strftime('%b %d'))
        if day_date in sales_map:
            monthly_chart_values.append(float(sales_map[day_date]['total_sales'] or 0))
        else:
            monthly_chart_values.append(0.0)

    # For the recent activity table, list all days in the month that had activity
    sales_by_date = list(monthly_sales_records.order_by('-day'))
    if not sales_by_date:
        sales_by_date = list(sales_qs.annotate(day=TruncDate('order_date')).values('day').annotate(
            total_sales=Sum('total_amount'),
            total_qty=Sum('quantity_kg'),
            total_orders=Count('id')
        ).order_by('-day')[:30])

    harvest_forecasts = filter_by_pond(
        request.user,
        HarvestForecast.objects.select_related('stock_batch'),
        'stock_batch__pond'
    ).order_by('predicted_harvest_date')[:5]

    sales_forecasts = SalesForecast.objects.select_related('species').order_by('period_start')[:5]
    upcoming_harvests = filter_by_pond(
        request.user,
        HarvestSchedule.objects.filter(status__in=[HarvestSchedule.Status.SCHEDULED, HarvestSchedule.Status.IN_PROGRESS]),
        'stock_batch__pond'
    ).count()
    if upcoming_harvests == 0:
        upcoming_harvests = active_ponds

    from apps.sales.models import Product
    total_products = Product.objects.filter(is_active=True).count()
    low_stock_count = Product.objects.filter(
        is_active=True,
        quantity_kg__lte=F('reorder_level_kg')
    ).count()
    recent_orders = SalesOrder.objects.select_related('customer', 'product').order_by('-created_at')[:6]
    
    from django.utils import timezone
    from django.db.models import Q

    today = timezone.now().date()
    azula_ponds = get_accessible_ponds(request.user).filter(
        Q(location__icontains='Azula') | Q(name__icontains='Azula'),
        transfer_date__isnull=False
    )
    
    azula_alerts = []
    for pond in azula_ponds:
        base_date = pond.last_sanitized_date or pond.transfer_date
        sanitization_date = base_date + timedelta(days=15)
        days_until = (sanitization_date - today).days
        
        if days_until < 0:
            status_text = f"Overdue by {abs(days_until)} days"
            badge_class = "bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse"
            dot_class = "bg-rose-500 animate-pulse"
            box_class = "border-rose-500/20 bg-rose-500/5"
            text_class = "text-rose-400"
        elif days_until == 0:
            status_text = "Due Today"
            badge_class = "bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse"
            dot_class = "bg-amber-400 animate-pulse"
            box_class = "border-amber-500/20 bg-amber-500/5"
            text_class = "text-amber-400"
        else:
            status_text = f"Due in {days_until} days"
            badge_class = "bg-cyan-500/10 text-cyan-300 border-cyan-500/20"
            dot_class = "bg-cyan-400"
            box_class = "border-cyan-500/20 bg-cyan-500/5"
            text_class = "text-cyan-400"

        azula_alerts.append({
            'pond': pond,
            'sanitization_date': sanitization_date,
            'last_sanitized_date': pond.last_sanitized_date,
            'days_until': days_until,
            'status_text': status_text,
            'badge_class': badge_class,
            'dot_class': dot_class,
            'box_class': box_class,
            'text_class': text_class,
        })

    if not azula_alerts:
        mock_date = today + timedelta(days=3)
        azula_alerts.append({
            'pond': {'name': 'Azula Sector 1', 'farm': {'name': 'Silay Superworm & Crayfish, Lantad Silay City'}, 'transfer_date': today - timedelta(days=12)},
            'sanitization_date': mock_date,
            'days_until': 3,
            'status_text': 'Due in 3 days',
            'badge_class': 'bg-cyan-500/10 text-cyan-300 border-cyan-500/20',
            'dot_class': 'bg-cyan-400',
            'box_class': 'border-cyan-500/20 bg-cyan-500/5',
            'text_class': 'text-cyan-400',
        })

    harvest_schedules_list = list(HarvestSchedule.objects.all().order_by('scheduled_date')[:1])
    harvest1 = harvest_schedules_list[0] if len(harvest_schedules_list) > 0 else None

    recent_orders_list = list(recent_orders[:2])
    order1 = recent_orders_list[0] if len(recent_orders_list) > 0 else None
    order2 = recent_orders_list[1] if len(recent_orders_list) > 1 else None

    # Pond Mortality Rates (Main Pond & Breeding Pond Product 1)
    from apps.operations.models import PondMortalityLog
    from django.db.models import Case, When, Value, IntegerField
    mortality_ponds_qs = accessible_ponds.filter(
        location__in=['Main Pond', 'Breeding Pond']
    ).annotate(
        loc_sort=Case(
            When(location='Main Pond', then=Value(1)),
            When(location='Breeding Pond', then=Value(2)),
            default=Value(3),
            output_field=IntegerField()
        )
    ).order_by('loc_sort', 'name')

    top_reason_stat = (
        PondMortalityLog.objects.filter(
            pond__in=mortality_ponds_qs
        )
        .exclude(product_name__icontains='Criling')
        .exclude(reason='')
        .values('reason')
        .annotate(count=Count('id'), total_qty=Sum('quantity'))
        .order_by('-count', '-total_qty')
        .first()
    )
    top_mortality_reason = top_reason_stat['reason'] if top_reason_stat else 'None Recorded'

    mortality_ponds = []
    for p in mortality_ponds_qs:
        stat_7d = p.get_mortality_stats(days=7)
        stat_30d = p.get_mortality_stats(days=30)
        prod = 'Breeder Crayfish' if p.location == 'Breeding Pond' else (p.product_name or 'Crayfish')
        mortality_ponds.append({
            'pond': p,
            'name': p.name,
            'location': p.location,
            'product_name': prod,
            'capacity': p.capacity or 0,
            'deaths': stat_30d['dead'],
            'rate_7d': stat_7d['rate'],
            'dead_7d': stat_7d['dead'],
            'rate_30d': stat_30d['rate'],
            'dead_30d': stat_30d['dead'],
        })

    total_dead_30d = sum(item['dead_30d'] for item in mortality_ponds)
    total_stock_all = sum(item['capacity'] for item in mortality_ponds) + total_dead_30d
    mortality_rate_30d = round((total_dead_30d / total_stock_all) * 100, 1) if total_stock_all > 0 else 0.0

    context = {
        'stats': {
            'total_farms': total_farms,
            'total_ponds': total_ponds,
            'active_ponds': active_ponds,
            'total_fish': total_fish,
            'total_biomass': total_biomass,
            'feed_used_30d': feed_used_30d,
            'feeding_count': feeding_count,
            'mortality_30d': total_dead_30d,
            'mortality_rate_30d': mortality_rate_30d,
            'mortality_events': mortality_events,
            'harvest_30d': harvest_30d,
            'harvest_count': harvest_count,
            'revenue_30d': revenue_30d,
            'order_count': order_count,
            'daily_sales_total': daily_sales_total,
            'pending_orders': pending_orders,
            'upcoming_harvests': upcoming_harvests,
            'total_products': total_products,
            'low_stock_alerts': low_stock_count,
        },
        'species_data': json.dumps(species_data),
        'farm_locations': json.dumps(farm_locations),
        'manager_info': manager_info,
        'analytics_embed': {
            'active_ponds': active_ponds,
            'total_fish_stock': total_fish,
            'monthly_revenue': revenue_30d,
            'monthly_harvest': harvest_30d,
        },
        'harvest_forecasts': harvest_forecasts,
        'sales_forecasts': sales_forecasts,
        'monthly_sales_total': monthly_sales['total_sales'] or 0,
        'monthly_sales_qty': monthly_sales['total_qty'] or 0,
        'monthly_expenses_total': 0,
        'sales_by_date': sales_by_date,
        'chart_labels': json.dumps(monthly_chart_labels),
        'chart_values': json.dumps(monthly_chart_values),
        'chart_month_name': month_name,
        'chart_days_count': f"{num_days} Days",
        'expenses_monthly': [],
        'recent_orders': recent_orders,
        'azula_alerts': azula_alerts,
        'harvest1': harvest1,
        'order1': order1,
        'order2': order2,
        'mortality_ponds': mortality_ponds,
        'top_mortality_reason': top_mortality_reason,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def inventory_overview(request):
    """Simple inventory list of species and feeds for accessible farms/ponds."""
    if is_customer(request.user):
        return redirect('sales:customer_portal')
    if is_rider(request.user):
        return redirect('sales:rider_portal')

    from apps.stock.models import StockBatch
    from apps.feed.models import FeedType

    active_batches = filter_by_pond(
        request.user,
        StockBatch.objects.filter(is_active=True).select_related('species', 'pond', 'pond__farm'),
        'pond'
    )

    species_inventory = []
    seen_species = set()
    for batch in active_batches:
        if batch.species_id in seen_species:
            continue
        seen_species.add(batch.species_id)
        species_inventory.append({
            'species_name': batch.species.name,
            'species_category': batch.species.get_category_display(),
        })
    species_inventory.sort(key=lambda item: item['species_name'])

    from apps.feed.models import FeedType, FeedSack, FeedStockMovement

    feed_inventory = []
    total_feed_sacks = Decimal('0')
    total_feed_weight_kg = Decimal('0.00')

    for feed_type in FeedType.objects.filter(is_active=True).prefetch_related('sacks').order_by('category', 'name'):
        kg_sack = feed_type.kg_per_sack or Decimal('0.00')
        all_sacks = list(feed_type.sacks.all().order_by('sack_number', 'created_at'))
        
        sacks_list = []
        if all_sacks:
            total_kg = sum((s.current_weight_kg for s in all_sacks), Decimal('0.000'))
            active_sacks_count = sum(1 for s in all_sacks if s.current_weight_kg > Decimal('0'))
            sacks_count = len(all_sacks)
            
            for s in all_sacks:
                sacks_list.append({
                    'id': s.id,
                    'sack_index': s.sack_number,
                    'sack_code': s.sack_code,
                    'initial_weight_kg': s.initial_weight_kg,
                    'weight_kg': s.current_weight_kg,
                    'status': s.status,
                    'status_color': s.status_color,
                    'percentage': s.percentage,
                })
        else:
            total_kg = max(Decimal('0.00'), feed_type.total_kg)
            sacks_count = int(round(float(feed_type.quantity_sacks or 0)))
            active_sacks_count = sacks_count

        total_feed_sacks += Decimal(str(active_sacks_count))
        total_feed_weight_kg += total_kg

        feed_inventory.append({
            'id': feed_type.id,
            'name': feed_type.name,
            'category': feed_type.get_category_display(),
            'raw_category': feed_type.category,
            'price_per_kg': feed_type.price_per_kg,
            'quantity_sacks': active_sacks_count,
            'total_sacks_count': len(sacks_list),
            'kg_per_sack': kg_sack,
            'total_kg': total_kg,
            'sacks_list': sacks_list,
            'has_sacks': len(sacks_list) > 0,
            'description': feed_type.description,
            'accent_color': feed_type.accent_color,
            'icon': feed_type.icon,
        })

    context = {
        'species_inventory': species_inventory,
        'feed_inventory': feed_inventory,
        'total_species_types': len(species_inventory),
        'total_feed_types': len(feed_inventory),
        'total_feed_sacks': total_feed_sacks,
        'total_feed_weight_kg': total_feed_weight_kg,
    }
    return render(request, 'inventory_management/list.html', context)


@login_required
def notifications(request):
    """Redirect to dashboard or portal since notifications page has been removed."""
    if is_customer(request.user):
        return redirect('sales:customer_portal')
    if is_rider(request.user):
        return redirect('sales:rider_portal')
    return redirect('dashboard')



# =============================================================================
# DATA ARCHIVE & RESTORE
# =============================================================================

ENTITY_MODEL_MAP = {
    'product': ('Product', 'apps.sales.models', 'Product Management', lambda p: p.name),
    'feed_type': ('FeedType', 'apps.feed.models', 'Feed Inventory', lambda f: f.name),
    'stock_batch': ('StockBatch', 'apps.stock.models', 'Stock Monitoring', lambda b: b.batch_code),
    'sales_order': ('SalesOrder', 'apps.sales.models', 'Sales Orders', lambda o: f"Order #{o.order_number}"),
}


@login_required
def archive_dashboard(request):
    """Redirect to the unified Audit & Bin dashboard tab."""
    tab = request.GET.get('tab', '')
    url = '/delivery-logs/?tab=bin'
    if tab:
        url += f'&bin_tab={tab}'
    return redirect(url)


@login_required
def archive_restore(request, entity_type, entity_id):
    """Restore a soft-deleted entity back to the active system."""
    if not (getattr(request.user, 'is_owner', False) or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Unauthorized action.')
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('/delivery-logs/?tab=bin')

    config = ENTITY_MODEL_MAP.get(entity_type)
    if not config:
        messages.error(request, f'Invalid entity type: {entity_type}')
        return redirect('/delivery-logs/?tab=bin')

    model_name, module_path, log_module, name_getter = config
    import importlib
    mod = importlib.import_module(module_path)
    model_class = getattr(mod, model_name)

    item = model_class.all_objects.filter(pk=entity_id, is_deleted=True).first()
    if not item:
        messages.error(request, f'{model_name} #{entity_id} not found in archive.')
        return redirect('/delivery-logs/?tab=bin')

    item_name = name_getter(item)
    item.restore()

    try:
        from apps.sales.models import InputLog
        InputLog.log(
            user=request.user,
            action=InputLog.Action.UPDATED,
            module='Bin',
            target_entity=f'{model_name}: {item_name}',
            details=f'Restored {item_name} from Bin back into active {log_module}.'
        )
    except Exception:
        pass

    messages.success(request, f'Successfully restored {item_name} back to active catalog!')
    tab_name = entity_type + ('es' if entity_type.endswith('ch') else 's')
    next_url = request.POST.get('next')
    return redirect(next_url or f"/delivery-logs/?tab=bin&bin_tab={tab_name}")


@login_required
def archive_hard_delete(request, entity_type, entity_id):
    """Permanently delete an entity from the database."""
    if not (getattr(request.user, 'is_owner', False) or request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'Unauthorized action.')
        return redirect('dashboard')

    if request.method != 'POST':
        return redirect('/delivery-logs/?tab=bin')

    config = ENTITY_MODEL_MAP.get(entity_type)
    if not config:
        messages.error(request, f'Invalid entity type: {entity_type}')
        return redirect('/delivery-logs/?tab=bin')

    model_name, module_path, log_module, name_getter = config
    import importlib
    mod = importlib.import_module(module_path)
    model_class = getattr(mod, model_name)

    item = model_class.all_objects.filter(pk=entity_id, is_deleted=True).first()
    if not item:
        messages.error(request, f'{model_name} #{entity_id} not found in archive.')
        return redirect('/delivery-logs/?tab=bin')

    item_name = name_getter(item)
    item.hard_delete()

    try:
        from apps.sales.models import InputLog
        InputLog.log(
            user=request.user,
            action=InputLog.Action.DELETED,
            module='Bin',
            target_entity=f'{model_name}: {item_name}',
            details=f'Permanently purged {item_name} from database.'
        )
    except Exception:
        pass

    messages.success(request, f'Permanently deleted {item_name}.')
    tab_name = entity_type + ('es' if entity_type.endswith('ch') else 's')
    next_url = request.POST.get('next')
    return redirect(next_url or f"/delivery-logs/?tab=bin&bin_tab={tab_name}")





