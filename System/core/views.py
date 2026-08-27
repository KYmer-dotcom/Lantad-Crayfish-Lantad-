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
import json
from apps.accounts.access import filter_by_pond, is_customer, is_rider, get_accessible_farms, get_accessible_ponds
from apps.accounts.models import User
from apps.sales.models import Customer


class CustomerRegistrationForm(forms.Form):
    CLASSIFICATION_CHOICES = [
        ('', 'Individual (default)'),
        ('market', 'Market'),
        ('restaurant', 'Restaurant'),
    ]

    username = forms.CharField(max_length=150)
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField(required=False)
    phone = forms.CharField(max_length=20)
    classification = forms.ChoiceField(required=False, choices=CLASSIFICATION_CHOICES)
    address = forms.CharField(widget=forms.Textarea)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean_phone(self):
        phone = self.cleaned_data['phone'].strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) != 11:
            raise forms.ValidationError('Phone number must be exactly 11 digits.')
        return digits

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    def save(self):
        username = self.cleaned_data['username'].strip()
        first_name = self.cleaned_data['first_name'].strip()
        last_name = self.cleaned_data['last_name'].strip()
        email = self.cleaned_data.get('email', '').strip()
        phone = self.cleaned_data['phone'].strip()
        classification = (self.cleaned_data.get('classification') or '').strip().lower()
        address = self.cleaned_data['address'].strip()

        user = User(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            role=User.Role.CUSTOMER,
            is_active=True,
        )
        user.set_password(self.cleaned_data['password1'])
        user.save()

        if classification == 'market':
            customer_type = Customer.Type.RETAILER
        elif classification == 'restaurant':
            customer_type = Customer.Type.RESTAURANT
        else:
            customer_type = Customer.Type.INDIVIDUAL

        Customer.objects.create(
            user=user,
            name=f"{first_name} {last_name}".strip() or username,
            customer_type=customer_type,
            contact_person=f"{first_name} {last_name}".strip(),
            phone=phone,
            email=email,
            address=address,
        )
        return user


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


def customer_register(request):
    """Dedicated registration page for customer accounts."""
    if request.user.is_authenticated:
        if is_customer(request.user):
            auth_logout(request)
        else:
            return redirect('dashboard')

    form = CustomerRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        auth_login(request, user)
        messages.success(request, 'Customer account created successfully.')
        return redirect('sales:customer_portal')

    return render(request, 'auth/customer_register.html', {'form': form})


def app_logout(request):
    """Role-aware logout redirect."""
    was_customer = request.user.is_authenticated and is_customer(request.user)
    auth_logout(request)
    if was_customer:
        return redirect('customer_login')
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
    
    # Date range for 30-day stats
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    
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
    
    orders_30d = SalesOrder.objects.filter(order_date__gte=thirty_days_ago, status='completed')
    revenue_30d = orders_30d.aggregate(total=Sum('total_amount'))['total'] or 0
    order_count = orders_30d.count()
    daily_sales_total = SalesOrder.objects.filter(order_date=datetime.now().date()).aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    pending_orders = SalesOrder.objects.exclude(status__in=['completed', 'cancelled']).count()
    
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
            'location': farm.location,
            'pin_color': 'admin',
            'is_current_account': True
        }
        for farm in accessible_farms
        if farm.location
    ]
    fixed_location_overrides = {
        'admin': 'Silay Superworm & Crayfish, Lantad Silay City',
        'farm 1': 'Balaring Silay City',
        'farm 2': 'EB magalona Negros Occidental',
    }
    for farm in farm_locations:
        lookup_key = farm['name'].strip().lower()
        if lookup_key in fixed_location_overrides:
            farm['location'] = fixed_location_overrides[lookup_key]

    # Embedded analytics + reports sections for dashboard
    sales_statuses = [SalesOrder.Status.DELIVERED, SalesOrder.Status.COMPLETED]
    sales_qs = SalesOrder.objects.filter(status__in=sales_statuses)
    latest_order = sales_qs.order_by('-order_date').first()
    ref_date = latest_order.order_date if latest_order else datetime.now().date()
    month_start = ref_date.replace(day=1)
    monthly_sales = sales_qs.filter(order_date__gte=month_start).aggregate(
        total_sales=Sum('total_amount'),
        total_qty=Sum('quantity_kg')
    )

    sales_by_date = sales_qs.annotate(day=TruncDate('order_date')).values('day').annotate(
        total_sales=Sum('total_amount'),
        total_qty=Sum('quantity_kg'),
        total_orders=Count('id')
    ).order_by('-day')[:10]

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
        sanitization_date = pond.transfer_date + timedelta(days=15)
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

    context = {
        'stats': {
            'total_farms': total_farms,
            'total_ponds': total_ponds,
            'active_ponds': active_ponds,
            'total_fish': total_fish,
            'total_biomass': total_biomass,
            'feed_used_30d': feed_used_30d,
            'feeding_count': feeding_count,
            'mortality_30d': mortality_30d,
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
        'expenses_monthly': [],
        'recent_orders': recent_orders,
        'azula_alerts': azula_alerts,
        'harvest1': harvest1,
        'order1': order1,
        'order2': order2,
    }
    
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def inventory_overview(request):
    """Simple inventory list of species and feeds for accessible farms/ponds."""
    if is_customer(request.user):
        return redirect('sales:customer_portal')

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

    feed_inventory = [
        {
            'id': feed_type.id,
            'name': feed_type.name,
            'category': feed_type.get_category_display(),
            'raw_category': feed_type.category,
            'price_per_kg': feed_type.price_per_kg,
            'description': feed_type.description,
            'accent_color': feed_type.accent_color,
            'icon': feed_type.icon,
        }
        for feed_type in FeedType.objects.filter(is_active=True).order_by('category', 'name')
    ]

    context = {
        'species_inventory': species_inventory,
        'feed_inventory': feed_inventory,
        'total_species_types': len(species_inventory),
        'total_feed_types': len(feed_inventory),
    }
    return render(request, 'inventory_management/list.html', context)


@login_required
def notifications(request):
    """Notifications center for alerts and reminders."""
    if is_customer(request.user):
        return redirect('sales:customer_portal')

    from apps.operations.models import Pond
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Q

    today = timezone.now().date()
    azula_ponds = get_accessible_ponds(request.user).filter(
        Q(location__icontains='Azula') | Q(name__icontains='Azula'),
        transfer_date__isnull=False
    )
    
    azula_alerts = []
    for pond in azula_ponds:
        sanitization_date = pond.transfer_date + timedelta(days=15)
        days_until = (sanitization_date - today).days
        
        if days_until < 0:
            status_text = f"Overdue by {abs(days_until)} days"
            badge_class = "bg-rose-500/10 text-rose-400 border-rose-500/20 animate-pulse"
            dot_class = "bg-rose-500 animate-pulse"
        elif days_until == 0:
            status_text = "Due Today"
            badge_class = "bg-amber-500/10 text-amber-400 border-amber-500/20 animate-pulse"
            dot_class = "bg-amber-400 animate-pulse"
        else:
            status_text = f"Due in {days_until} days"
            badge_class = "bg-cyan-500/10 text-cyan-300 border-cyan-500/20"
            dot_class = "bg-cyan-400"

        azula_alerts.append({
            'pond': pond,
            'sanitization_date': sanitization_date,
            'days_until': days_until,
            'status_text': status_text,
            'badge_class': badge_class,
            'dot_class': dot_class,
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
        })

    from apps.harvest.models import HarvestSchedule
    harvest_schedules = list(HarvestSchedule.objects.all().order_by('scheduled_date')[:1])
    harvest1 = harvest_schedules[0] if len(harvest_schedules) > 0 else None

    from apps.sales.models import SalesOrder
    recent_orders = list(SalesOrder.objects.all().order_by('-created_at')[:2])
    order1 = recent_orders[0] if len(recent_orders) > 0 else None
    order2 = recent_orders[1] if len(recent_orders) > 1 else None

    context = {
        'azula_alerts': azula_alerts,
        'alerts': [],
        'order1': order1,
        'order2': order2,
        'harvest1': harvest1,
    }
    return render(request, 'notifications/index.html', context)
