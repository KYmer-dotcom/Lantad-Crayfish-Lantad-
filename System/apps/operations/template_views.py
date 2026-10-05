"""
Template views for Ponds module
"""
import re

def natural_sort_key(pond):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', pond.name)]

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib import messages
from django import forms
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.utils import timezone
import json

from apps.accounts.access import get_accessible_farms, get_accessible_ponds, is_owner, ensure_not_customer
from apps.accounts.models import User
from apps.stock.models import Species
from apps.feed.models import FeedType
from .models import Farm, Pond, PondFeedingLog


class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Farm name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Location'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
        }


class PondForm(forms.ModelForm):
    transfer_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none'
        }),
        required=False,
        label="Date Transferred"
    )
    product_name = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none'
        }),
        label="Product"
    )
    product_name_2 = forms.ChoiceField(
        choices=[],
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none'
        }),
        label="Product 2"
    )
    capacity_2 = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none',
            'placeholder': 'Quantity 2',
            'min': 0,
        }),
        label="Quantity 2"
    )
    category = forms.ChoiceField(
        choices=[
            ('Main Pond', 'Main Pond'),
            ('Breeding Pond', 'Breeding Pond'),
            ('Superworm Cabin', 'Superworm Cabin'),
            ('Azula', 'Azula')
        ],
        widget=forms.Select(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none'
        }),
        label="Category"
    )
    shelf_position = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    status = forms.ChoiceField(
        choices=[
            ('active', 'Active'),
            ('empty', 'Unused'),
            ('maintenance', 'Under Maintenance')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none'
        }),
        label="Status"
    )
    class Meta:
        model = Pond
        fields = ['name', 'capacity', 'product_name', 'capacity_2', 'product_name_2', 'transfer_date', 'shelf_position', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none uppercase',
                'placeholder': 'Name'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none',
                'placeholder': 'Quantity',
                'min': 0,
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['capacity'].min_value = 0
        self.fields['capacity'].required = False
        self.fields['capacity_2'].min_value = 0
        self.fields['capacity_2'].required = False
        from apps.sales.models import Product
        products = Product.objects.filter(is_active=True).order_by('name')
        product_choices = [('', '---------')] + [(p.name, p.name) for p in products]
        self.fields['product_name'].choices = product_choices
        self.fields['product_name_2'].choices = product_choices

    def clean_name(self):
        return self.cleaned_data.get('name', '').upper()

    def clean_transfer_date(self):
        return self.cleaned_data.get('transfer_date')

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        capacity = cleaned_data.get('capacity')
        product_name = cleaned_data.get('product_name')
        product_name_2 = cleaned_data.get('product_name_2')
        
        if category == 'Breeding Pond':
            if product_name and product_name_2 and product_name == product_name_2:
                self.add_error('product_name_2', 'Product 1 and Product 2 cannot be the same product.')
        elif category == 'Superworm Cabin':
            # Skip standard capacity for Superworm Cabin, handled via shelf_position
            pass
        else:
            if capacity is None:
                self.add_error('capacity', 'Quantity is required.')
                
        return cleaned_data


@login_required
def ponds_list(request):
    """List all farms and ponds"""
    farms = get_accessible_farms(request.user)
    ponds = get_accessible_ponds(request.user).select_related('farm').prefetch_related('species')
    from django.utils import timezone
    today = timezone.now().date()
    today_logs = {log.pond_id: log for log in PondFeedingLog.objects.filter(recorded_at__date=today)}
    
    superworm_ponds = ponds.filter(location='Superworm Cabin')
    sw_block1_ponds = sorted(list(superworm_ponds.filter(shelf_position='Left Shelf')), key=natural_sort_key)
    sw_block2_ponds = sorted(list(superworm_ponds.filter(shelf_position='Right Shelf')), key=natural_sort_key)
    sw_block3_ponds = sorted(list(superworm_ponds.filter(shelf_position='Back Shelf')), key=natural_sort_key)

    breeding_ponds = sorted(list(ponds.filter(location='Breeding Pond')), key=natural_sort_key)
    breeding_crilings_ponds = [p for p in breeding_ponds if p.breeding_type == 'Crilings']
    breeding_reproduction_ponds = [p for p in breeding_ponds if p.breeding_type != 'Crilings']
    main_ponds = sorted(list(ponds.filter(location='Main Pond') | ponds.filter(location='')), key=natural_sort_key)
    azula_ponds_list = list(ponds.filter(location='Azula'))
    azula_ponds = {p.shelf_position: p for p in azula_ponds_list}
    azula_active_ponds = sorted([p for p in azula_ponds_list if p.status == 'active'], key=natural_sort_key)

    # Attach today_log to all finalized list elements in Python
    all_finalized = sw_block1_ponds + sw_block2_ponds + sw_block3_ponds + breeding_ponds + main_ponds + azula_ponds_list
    for p in all_finalized:
        p.today_log = today_logs.get(p.id)

    outdoor_ponds_count = len(main_ponds) + len(breeding_ponds)
    cabin_ponds_count = superworm_ponds.count()
    azula_ponds_count = len(azula_ponds)

    # Check if operations have already been recorded today for each category (fully complete for all ponds)
    main_pond_recorded_today = len(main_ponds) > 0 and all(
        PondFeedingLog.objects.filter(pond=p, recorded_at__date=today).exists() for p in main_ponds
    )
    breeding_pond_recorded_today = len(breeding_ponds) > 0 and all(
        PondFeedingLog.objects.filter(pond=p, recorded_at__date=today).exists() for p in breeding_ponds
    )
    superworm_cabin_recorded_today = superworm_ponds.exists() and all(
        PondFeedingLog.objects.filter(pond=p, recorded_at__date=today).exists() for p in superworm_ponds
    )
    azula_sanitized_today = len(azula_active_ponds) > 0 and all(
        p.last_sanitized_date == today for p in azula_active_ponds
    )
    azula_due_count = sum(1 for p in azula_active_ponds if p.is_sanitization_due)
    azula_all_up_to_date = len(azula_active_ponds) > 0 and azula_due_count == 0

    context = {
        'farms': farms,
        'ponds': ponds, # all ponds
        'main_ponds': main_ponds,
        'breeding_ponds': breeding_ponds,
        'breeding_crilings_ponds': breeding_crilings_ponds,
        'breeding_reproduction_ponds': breeding_reproduction_ponds,
        'outdoor_ponds_count': outdoor_ponds_count,
        'cabin_ponds_count': cabin_ponds_count,
        'azula_ponds_count': azula_ponds_count,
        'sw_block1_ponds': sw_block1_ponds,
        'sw_block2_ponds': sw_block2_ponds,
        'sw_block3_ponds': sw_block3_ponds,
        'azula_ponds': azula_ponds,
        'azula_active_ponds': azula_active_ponds,
        'farm_form': FarmForm(),
        'pond_form': PondForm(user=request.user),
        'feed_types': FeedType.objects.filter(is_active=True).order_by('category', 'name'),
        'main_pond_recorded_today': main_pond_recorded_today,
        'breeding_pond_recorded_today': breeding_pond_recorded_today,
        'superworm_cabin_recorded_today': superworm_cabin_recorded_today,
        'azula_sanitized_today': azula_sanitized_today,
        'azula_due_count': azula_due_count,
        'azula_all_up_to_date': azula_all_up_to_date,
        'today': today,
    }
    return render(request, 'operations/list.html', context)


@login_required
def farm_create(request):
    ensure_not_customer(request.user)
    if request.method != 'POST':
        return redirect('ponds:list')

    form = FarmForm(request.POST)
    if form.is_valid():
        farm = form.save(commit=False)
        farm.owner = request.user
        farm.total_area = farm.total_area or 0
        farm.save()
        messages.success(request, f'Farm "{farm.name}" created successfully!')

        if request.htmx:
            farms = get_accessible_farms(request.user)
            return render(request, 'operations/partials/farm_update.html', {
                'farms': farms,
                'pond_form': PondForm(user=request.user),
            })
        return redirect('ponds:list')

    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    return redirect('ponds:list')


@login_required
def pond_create(request):
    ensure_not_customer(request.user)
    if request.method != 'POST':
        return redirect('ponds:list')

    form = PondForm(request.POST, user=request.user)
    if form.is_valid():
        pond = form.save(commit=False)
        category = form.cleaned_data.get('category') or 'Main Pond'
        pond.location = category
        pond.capacity = pond.capacity or 0
        pond.capacity_2 = pond.capacity_2 or 0
        pond.female_quantity = pond.female_quantity or 0
        pond.size = pond.size or 0
        pond.depth = pond.depth or 0
        if not pond.status:
            pond.status = Pond.Status.ACTIVE if (pond.capacity > 0 or pond.capacity_2 > 0) else Pond.Status.EMPTY

        farm = get_accessible_farms(request.user).first()
        if not farm:
            farm = Farm.objects.create(
                name="Default Farm",
                location="",
                total_area=0,
                owner=request.user,
                description="",
            )
        pond.farm = farm
        pond.save()
        messages.success(request, f'Record "{pond.name}" created successfully!')

        if request.htmx:
            ponds = get_accessible_ponds(request.user).select_related('farm').prefetch_related('species')
            farms = get_accessible_farms(request.user) if is_owner(request.user) else None
            return render(request, 'operations/partials/ponds_update.html', {
                'ponds': ponds,
                'farms': farms,
            })

        if category == 'Azula':
            return redirect(reverse('ponds:list') + '?type=azula')
        if category == 'Superworm Cabin':
            return redirect(reverse('ponds:list') + '?type=cabin')
        return redirect('ponds:list')

    for field, errors in form.errors.items():
        for error in errors:
            messages.error(request, f"{field}: {error}")
    category = request.POST.get('category')
    if category == 'Azula':
        return redirect(reverse('ponds:list') + '?type=azula')
    if category == 'Superworm Cabin':
        return redirect(reverse('ponds:list') + '?type=cabin')
    return redirect('ponds:list')
@login_required
def pond_edit(request, pond_id):
    """Edit a pond"""
    
    pond = get_object_or_404(get_accessible_ponds(request.user), pk=pond_id)
    
    # Determine the category type (azula, cabin, or pond)
    target_type = request.GET.get('type')
    if not target_type:
        if pond.location == 'Azula':
            target_type = 'azula'
        elif pond.location == 'Superworm Cabin':
            target_type = 'cabin'
        else:
            target_type = 'pond'

    if request.method == 'POST':
        form = PondForm(request.POST, instance=pond, user=request.user)
        if form.is_valid():
            pond = form.save(commit=False)
            pond.location = form.cleaned_data.get('category', 'Main Pond')
            pond.save()
            messages.success(request, f'Record "{pond.name}" updated successfully!')
            if pond.location == 'Azula':
                return redirect(reverse('ponds:list') + '?type=azula')
            if pond.location == 'Superworm Cabin':
                return redirect(reverse('ponds:list') + '?type=cabin')
            return redirect('ponds:list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        initial_data = {'category': pond.location or 'Main Pond'}
        form = PondForm(instance=pond, initial=initial_data, user=request.user)
        
    cancel_url = reverse('ponds:list')
    if target_type == 'azula':
        cancel_url += '?type=azula'
    elif target_type == 'cabin':
        cancel_url += '?type=cabin'

    return render(request, 'operations/edit.html', {
        'form': form, 
        'pond': pond,
        'current_op_type': target_type,
        'cancel_url': cancel_url,
    })


@login_required
def farm_remove(request, farm_id):
    """Remove a farm (owner only)."""
    if not is_owner(request.user):
        raise PermissionDenied("Only owners can remove farms.")

    farm = get_object_or_404(Farm, pk=farm_id)
    farm_name = farm.name
    farm.delete()
    messages.success(request, f'Farm "{farm_name}" removed successfully.')

    if request.htmx:
        farms = get_accessible_farms(request.user)
        return render(request, 'operations/partials/farm_update.html', {
            'farms': farms,
            'pond_form': PondForm(user=request.user),
        })

    return redirect('ponds:list')


@login_required
def pond_remove(request, pond_id):
    """Remove a pond (owner or assigned manager)."""

    pond = get_object_or_404(get_accessible_ponds(request.user), pk=pond_id)
    pond_name = pond.name
    pond_location = pond.location
    pond.delete()
    messages.success(request, f'Pond "{pond_name}" removed successfully.')

    if request.htmx:
        ponds = get_accessible_ponds(request.user).select_related('farm').prefetch_related('species')
        farms = get_accessible_farms(request.user) if is_owner(request.user) else None
        return render(request, 'operations/partials/ponds_update.html', {
            'ponds': ponds,
            'farms': farms,
        })

    if pond_location == 'Azula':
        return redirect(reverse('ponds:list') + '?type=azula')
    if pond_location == 'Superworm Cabin':
        return redirect(reverse('ponds:list') + '?type=cabin')
    return redirect('ponds:list')


@login_required
def pond_geomap(request):
    ponds = get_accessible_ponds(request.user).select_related('farm').order_by('farm__name', 'name')
    map_points = []

    for pond in ponds:
        location = (pond.location or '').strip()
        match = re.search(r'(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)', location)
        if not match:
            continue
        lat = float(match.group(1))
        lng = float(match.group(2))
        if lat < -90 or lat > 90 or lng < -180 or lng > 180:
            continue
        map_points.append({
            'pond': pond.name,
            'farm': pond.farm.name if pond.farm else 'Unassigned',
            'caretaker': pond.caretaker_name or 'Unassigned',
            'location': location,
            'lat': lat,
            'lng': lng,
        })

    context = {
        'map_points': map_points,
        'pond_count': ponds.count(),
    }
    return render(request, 'operations/geomap.html', context)


@login_required
def operations_data(request):
    """View operations data separated by Ponds and Superworm Cabin"""
    ponds = get_accessible_ponds(request.user).select_related('farm').prefetch_related('species')
    from django.utils import timezone
    today = timezone.now().date()
    today_logs = {log.pond_id: log for log in PondFeedingLog.objects.filter(recorded_at__date=today)}
    for pond in ponds:
        pond.today_log = today_logs.get(pond.id)
    
    # "first is the Pond below that is the superworm cabin"
    # We group Main Pond and Breeding Pond under "Pond", and Superworm Cabin separately.
    main_ponds = ponds.filter(location='Main Pond') | ponds.filter(location='')
    breeding_ponds = ponds.filter(location='Breeding Pond')
    
    superworm_ponds = ponds.filter(location='Superworm Cabin')
    sw_block1_ponds = superworm_ponds.filter(shelf_position='Left Shelf')
    sw_block2_ponds = superworm_ponds.filter(shelf_position='Right Shelf')
    sw_block3_ponds = superworm_ponds.filter(shelf_position='Back Shelf')

    context = {
        'main_ponds': sorted(list(main_ponds), key=natural_sort_key),
        'breeding_ponds': sorted(list(breeding_ponds), key=natural_sort_key),
        'sw_block1_ponds': sorted(list(sw_block1_ponds), key=natural_sort_key),
        'sw_block2_ponds': sorted(list(sw_block2_ponds), key=natural_sort_key),
        'sw_block3_ponds': sorted(list(sw_block3_ponds), key=natural_sort_key),
        'azula_ponds': {p.shelf_position: p for p in ponds.filter(location='Azula')},
        'feed_types': FeedType.objects.filter(is_active=True).order_by('category', 'name'),
    }
    return render(request, 'operations/operations.html', context)


@login_required
@require_POST
def record_operations(request):
    """Save pond operations logs"""
    try:
        from django.utils import timezone
        today = timezone.now().date()
        
        data = json.loads(request.body)
        logs = data.get('logs', [])
        recorded_count = 0
        for log in logs:
            pond_id = log.get('pond_id')
            fed = log.get('fed', False)
            feed_type_id = log.get('feed_type_id') or None
            
            pond = get_object_or_404(get_accessible_ponds(request.user), pk=pond_id)
            
            # Prevent double entries for the same day
            if PondFeedingLog.objects.filter(pond=pond, recorded_at__date=today).exists():
                continue
                
            PondFeedingLog.objects.create(
                pond=pond,
                feed_type_id=feed_type_id,
                fed=fed,
                recorded_by=request.user
            )
            recorded_count += 1
        return JsonResponse({'status': 'success', 'recorded_count': recorded_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def mark_pond_sanitized(request, pond_id):
    ensure_not_customer(request.user)
    pond = get_object_or_404(get_accessible_ponds(request.user), pk=pond_id)
    
    if not pond.is_sanitization_due:
        messages.warning(request, f"{pond.name} is not yet due for sanitization (available in {pond.sanitization_days_remaining} days).")
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return redirect(referer)
        return redirect('notifications')
    
    from django.utils import timezone
    today = timezone.now().date()
    pond.last_sanitized_date = today
    if pond.status == Pond.Status.MAINTENANCE:
        pond.status = Pond.Status.ACTIVE
    pond.save()
    
    # Audit trail
    try:
        from apps.sales.models import InputLog
        InputLog.log(
            user=request.user,
            module='Operations',
            action='sanitized',
            target_entity=f"Pond {pond.name}",
            change_details=f"Pond {pond.name} marked as sanitized on {today}. Next sanitization due in 15 days."
        )
    except Exception:
        pass
        
    messages.success(request, f"{pond.name} has been marked as sanitized. Next cycle due in 15 days.")
    
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('notifications')


@login_required
@require_POST
def record_azula_sanitization(request):
    ensure_not_customer(request.user)
    try:
        from django.utils import timezone
        today = timezone.now().date()
        data = json.loads(request.body)
        pond_ids = data.get('pond_ids', [])
        
        sanitized_names = []
        skipped_names = []
        for pid in pond_ids:
            pond = get_object_or_404(get_accessible_ponds(request.user), pk=pid)
            if not pond.is_sanitization_due:
                skipped_names.append(pond.name)
                continue
            pond.last_sanitized_date = today
            if pond.status == Pond.Status.MAINTENANCE:
                pond.status = Pond.Status.ACTIVE
            pond.save()
            sanitized_names.append(pond.name)
            
            # Audit trail
            try:
                from apps.sales.models import InputLog
                InputLog.log(
                    user=request.user,
                    module='Operations',
                    action='sanitized',
                    target_entity=f"Pond {pond.name}",
                    change_details=f"Azula tank {pond.name} sanitized on {today} via Operations Sidebar."
                )
            except Exception:
                pass
                
        if not sanitized_names and skipped_names:
            return JsonResponse({
                'status': 'error',
                'message': "Selected tank(s) are not yet due for sanitization (15-day cycle not reached)."
            }, status=400)

        return JsonResponse({
            'status': 'success',
            'sanitized_count': len(sanitized_names),
            'message': f"Successfully recorded sanitization for {len(sanitized_names)} Azula tank(s). Next cycle due in 15 days."
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
@require_POST
def pond_transfer(request):
    """Transfer stock from one pond (e.g. Breeding Pond) to a destination pond (e.g. Main Pond)."""
    ensure_not_customer(request.user)
    accessible_ponds = get_accessible_ponds(request.user)
    
    source_pond_id = request.POST.get('source_pond_id')
    dest_pond_id = request.POST.get('destination_pond_id')
    target_product = request.POST.get('target_product', '1')
    transfer_qty_str = request.POST.get('transfer_quantity')
    
    referer = request.META.get('HTTP_REFERER')
    redirect_target = referer if referer else 'ponds:list'
    
    if not source_pond_id or not dest_pond_id:
        messages.error(request, "Please select both a source pond and a destination Main Pond.")
        return redirect(redirect_target)
        
    source_pond = get_object_or_404(accessible_ponds, id=source_pond_id)
    dest_pond = get_object_or_404(accessible_ponds, id=dest_pond_id)
    
    if source_pond.id == dest_pond.id:
        messages.error(request, "Source and destination ponds cannot be the same.")
        return redirect(redirect_target)
        
    # Determine which product and available quantity
    if target_product == '2':
        prod_name = source_pond.product_name_2 or "Crilings"
        available_qty = source_pond.capacity_2 or 0
    else:
        prod_name = source_pond.product_name or "Stock"
        available_qty = source_pond.capacity or 0
        
    try:
        transfer_qty = int(transfer_qty_str) if transfer_qty_str else available_qty
    except ValueError:
        transfer_qty = available_qty
        
    if transfer_qty <= 0:
        messages.error(request, "Transfer quantity must be greater than 0.")
        return redirect(redirect_target)
        
    if transfer_qty > available_qty:
        messages.error(request, f"Cannot transfer {transfer_qty}. Only {available_qty} available in {source_pond.name}.")
        return redirect(redirect_target)
        
    # Deduct from source pond
    if target_product == '2':
        source_pond.capacity_2 -= transfer_qty
        if source_pond.capacity_2 <= 0:
            source_pond.capacity_2 = 0
            source_pond.product_name_2 = ''
        source_pond.save()
    else:
        source_pond.capacity -= transfer_qty
        if source_pond.capacity <= 0:
            if source_pond.product_name_2 and source_pond.capacity_2:
                source_pond.product_name = source_pond.product_name_2
                source_pond.capacity = source_pond.capacity_2
                source_pond.product_name_2 = ''
                source_pond.capacity_2 = 0
            else:
                source_pond.capacity = 0
                source_pond.status = Pond.Status.EMPTY
                source_pond.transfer_date = None
        source_pond.save()
        
    # Add to destination pond
    dest_pond.product_name = prod_name
    dest_pond.capacity = (dest_pond.capacity or 0) + transfer_qty
    dest_pond.status = Pond.Status.ACTIVE
    dest_pond.transfer_date = timezone.localdate() if hasattr(timezone, 'localdate') else timezone.now().date()
    dest_pond.save()
    
    # Audit log if available
    try:
        from apps.sales.models import InputLog
        InputLog.log(
            user=request.user,
            module='Operations',
            action='transferred',
            target_entity=f"{source_pond.name} -> {dest_pond.name}",
            change_details=f"Transferred {transfer_qty} {prod_name} from {source_pond.name} to {dest_pond.name}."
        )
    except Exception:
        pass
    
    messages.success(
        request, 
        f"Successfully transferred {transfer_qty} {prod_name} from {source_pond.name} to {dest_pond.name}!"
    )
    return redirect(redirect_target)




