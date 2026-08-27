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
    breeding_type = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('Reproduction', 'Reproduction'),
            ('Crilings', 'Crilings')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none'
        }),
        label="Type"
    )

    female_quantity = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-slate-200 px-4 py-3 text-sm focus:border-cyan-300 focus:outline-none',
            'placeholder': 'Female Quantity',
            'min': 0,
        }),
        label="Female Quantity"
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
        fields = ['name', 'capacity', 'product_name', 'transfer_date', 'breeding_type', 'female_quantity', 'shelf_position', 'status']
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
        from apps.sales.models import Product
        products = Product.objects.filter(is_active=True).order_by('name')
        self.fields['product_name'].choices = [('', '---------')] + [(p.name, p.name) for p in products]

    def clean_name(self):
        return self.cleaned_data.get('name', '').upper()

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        breeding_type = cleaned_data.get('breeding_type')
        capacity = cleaned_data.get('capacity')
        female_quantity = cleaned_data.get('female_quantity')
        
        if category == 'Breeding Pond':
            if not breeding_type:
                self.add_error('breeding_type', 'Type is required for Breeding Ponds.')
            
            if breeding_type == 'Reproduction':
                if female_quantity is None:
                    self.add_error('female_quantity', 'Female quantity is required for Reproduction ponds.')
            else:
                if capacity is None:
                    self.add_error('capacity', 'Quantity is required.')
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
    main_ponds = sorted(list(ponds.filter(location='Main Pond') | ponds.filter(location='')), key=natural_sort_key)
    azula_ponds_list = list(ponds.filter(location='Azula'))
    azula_ponds = {p.shelf_position: p for p in azula_ponds_list}

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

    context = {
        'farms': farms,
        'ponds': ponds, # all ponds
        'main_ponds': main_ponds,
        'breeding_ponds': breeding_ponds,
        'outdoor_ponds_count': outdoor_ponds_count,
        'cabin_ponds_count': cabin_ponds_count,
        'azula_ponds_count': azula_ponds_count,
        'sw_block1_ponds': sw_block1_ponds,
        'sw_block2_ponds': sw_block2_ponds,
        'sw_block3_ponds': sw_block3_ponds,
        'azula_ponds': azula_ponds,
        'farm_form': FarmForm(),
        'pond_form': PondForm(user=request.user),
        'feed_types': FeedType.objects.filter(is_active=True).order_by('category', 'name'),
        'main_pond_recorded_today': main_pond_recorded_today,
        'breeding_pond_recorded_today': breeding_pond_recorded_today,
        'superworm_cabin_recorded_today': superworm_cabin_recorded_today,
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
        pond.female_quantity = pond.female_quantity or 0
        pond.size = pond.size or 0
        pond.depth = pond.depth or 0
        if not pond.status:
            pond.status = Pond.Status.ACTIVE if pond.capacity > 0 else Pond.Status.EMPTY

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
    
    if request.method == 'POST':
        form = PondForm(request.POST, instance=pond, user=request.user)
        if form.is_valid():
            pond = form.save(commit=False)
            pond.location = form.cleaned_data.get('category', 'Main Pond')
            pond.save()
            messages.success(request, f'Record "{pond.name}" updated successfully!')
            if pond.location == 'Azula':
                return redirect(reverse('ponds:list') + '?type=azula')
            return redirect('ponds:list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        initial_data = {'category': pond.location or 'Main Pond'}
        form = PondForm(instance=pond, initial=initial_data, user=request.user)
        
    return render(request, 'operations/edit.html', {'form': form, 'pond': pond})


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


