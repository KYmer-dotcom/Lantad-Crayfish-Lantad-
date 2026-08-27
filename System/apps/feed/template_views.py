"""
Template views for Feed module
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django import forms
from django.db import transaction
from django.utils import timezone

from apps.accounts.access import filter_by_pond, ensure_not_customer, get_accessible_ponds
from .models import FeedingLog, FeedType, FeedStockMovement
from .services import consume_feed
from apps.stock.models import StockBatch


class FeedingLogForm(forms.ModelForm):
    class Meta:
        model = FeedingLog
        fields = ['stock_batch', 'feed_type', 'quantity_kg', 'feeding_time', 'notes']
        widgets = {
            'stock_batch': forms.Select(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none'
            }),
            'feed_type': forms.Select(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none',
                'placeholder': 'Quantity (kg)',
                'step': '0.01'
            }),
            'feeding_time': forms.HiddenInput(),
            'notes': forms.Textarea(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none',
                'rows': 2,
                'placeholder': 'Notes (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['feeding_time'].required = False
        if user:
            self.fields['stock_batch'].queryset = filter_by_pond(
                user,
                StockBatch.objects.select_related('pond', 'species'),
                'pond'
            )


class FeedStockForm(forms.Form):
    feed_type = forms.ModelChoiceField(
        queryset=FeedType.objects.filter(is_active=True).order_by('category', 'name'),
        widget=forms.Select(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none'
        })
    )
    quantity_kg = forms.DecimalField(
        min_value=0.01,
        decimal_places=2,
        max_digits=10,
        widget=forms.NumberInput(attrs={
            'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none',
            'placeholder': 'Quantity (kg)',
            'step': '0.01',
        })
    )


class FeedTypeForm(forms.ModelForm):
    class Meta:
        model = FeedType
        fields = ['name', 'brand', 'category', 'price_per_kg', 'description', 'accent_color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none',
                'placeholder': 'Feed name'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none',
                'placeholder': 'Brand (optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none'
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 focus:border-[#cca43b] focus:outline-none',
                'placeholder': 'Price per kg',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'mt-2 w-full rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-stone-100 placeholder:text-stone-500 focus:border-[#cca43b] focus:outline-none',
                'rows': 3,
                'placeholder': 'Brief description of this feed...'
            }),
            'accent_color': forms.HiddenInput(),
            'icon': forms.HiddenInput(),
        }


def _build_feed_pond_rows(user):
    ponds = get_accessible_ponds(user).select_related('farm').order_by('farm__name', 'name')
    stock_batches = filter_by_pond(
        user,
        StockBatch.objects.filter(is_active=True).select_related('pond', 'species'),
        'pond'
    ).order_by('pond__name', 'batch_code')

    batches_by_pond = {}
    for batch in stock_batches:
        batches_by_pond.setdefault(batch.pond_id, []).append(batch)

    latest_by_pond = {}
    latest_logs = FeedingLog.objects.filter(
        stock_batch__pond__in=ponds,
        stock_batch__is_active=True,
    ).select_related('feed_type', 'stock_batch').order_by('stock_batch__pond_id', '-feeding_time')
    for log in latest_logs:
        pond_id = log.stock_batch.pond_id
        if pond_id not in latest_by_pond:
            latest_by_pond[pond_id] = log

    today = timezone.localdate()
    fed_today_pond_ids = set(
        FeedingLog.objects.filter(
            stock_batch__pond__in=ponds,
            feeding_time__date=today
        ).values_list('stock_batch__pond_id', flat=True).distinct()
    )

    feed_pond_rows = []
    for pond in ponds:
        pond_batches = batches_by_pond.get(pond.id, [])
        latest_log = latest_by_pond.get(pond.id)
        default_batch = None
        if latest_log and latest_log.stock_batch and latest_log.stock_batch.is_active:
            default_batch = latest_log.stock_batch
        elif pond_batches:
            default_batch = pond_batches[0]
        feed_pond_rows.append({
            'pond': pond,
            'default_batch_id': default_batch.id if default_batch else '',
            'default_feed_type_id': latest_log.feed_type_id if latest_log else '',
            'fed_today': pond.id in fed_today_pond_ids,
            'has_active_batch': bool(pond_batches),
        })

    return feed_pond_rows, stock_batches, ponds


@login_required
def feed_list(request):
    """List feeding logs."""
    ensure_not_customer(request.user)
    feeding_logs = filter_by_pond(
        request.user,
        FeedingLog.objects.select_related('stock_batch', 'feed_type', 'fed_by'),
        'stock_batch__pond'
    )[:50]
    feed_pond_rows, stock_batches, _ = _build_feed_pond_rows(request.user)
    feed_types = FeedType.objects.filter(is_active=True).order_by('category', 'name')
    feed_stock_movements = FeedStockMovement.objects.select_related(
        'feed_type', 'moved_by'
    ).order_by('-moved_at')[:50]

    context = {
        'feeding_logs': feeding_logs,
        'stock_batches': stock_batches,
        'feed_pond_rows': feed_pond_rows,
        'feed_types': feed_types,
        'feed_stock_movements': feed_stock_movements,
        'feeding_log_form': FeedingLogForm(user=request.user),
        'feed_stock_form': FeedStockForm(),
        'feed_type_form': FeedTypeForm(),
    }
    return render(request, 'feed/list.html', context)


@login_required
def feeding_log_create(request):
    """Create a new feeding log"""
    ensure_not_customer(request.user)
    if request.method == 'POST':
        form = FeedingLogForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic():
                    feeding_log = form.save(commit=False)
                    if not feeding_log.feeding_time:
                        feeding_log.feeding_time = timezone.now()
                    feeding_log.fed_by = request.user
                    feeding_log.save()
                    consume_feed(
                        feed_type=feeding_log.feed_type,
                        quantity_kg=feeding_log.quantity_kg,
                        user=request.user,
                        feeding_log=feeding_log,
                    )
            except ValidationError as exc:
                messages.error(request, str(exc))
                return redirect('feed:list')
            messages.success(request, 'Feeding log recorded successfully!')
            
            if request.htmx:
                feeding_logs = filter_by_pond(
                    request.user,
                    FeedingLog.objects.select_related('stock_batch', 'feed_type', 'fed_by'),
                    'stock_batch__pond'
                )[:50]
                feed_pond_rows, _, _ = _build_feed_pond_rows(request.user)
                feed_stock_movements = FeedStockMovement.objects.select_related(
                    'feed_type', 'moved_by'
                ).order_by('-moved_at')[:50]
                return render(request, 'feed/partials/feeding_update.html', {
                    'feeding_logs': feeding_logs,
                    'feed_pond_rows': feed_pond_rows,
                    'feed_stock_movements': feed_stock_movements,
                })
            
            return redirect('feed:list')
    else:
        form = FeedingLogForm(user=request.user)
    
    if request.htmx:
        feeding_logs = filter_by_pond(
            request.user,
            FeedingLog.objects.select_related('stock_batch', 'feed_type', 'fed_by'),
            'stock_batch__pond'
        )[:50]
        feed_pond_rows, _, _ = _build_feed_pond_rows(request.user)
        feed_stock_movements = FeedStockMovement.objects.select_related(
            'feed_type', 'moved_by'
        ).order_by('-moved_at')[:50]
        return render(request, 'feed/partials/feeding_update.html', {
            'feeding_logs': feeding_logs,
            'feed_pond_rows': feed_pond_rows,
            'feed_stock_movements': feed_stock_movements,
        })
    
    return redirect('feed:list')


@login_required
def feed_stock_add(request):
    """Add feed stock quantity using existing feed types."""
    ensure_not_customer(request.user)
    if request.method != 'POST':
        return redirect('feed:list')

    form = FeedStockForm(request.POST)
    if form.is_valid():
        feed_type = form.cleaned_data['feed_type']
        quantity_kg = form.cleaned_data['quantity_kg']
        FeedStockMovement.objects.create(
            feed_type=feed_type,
            movement_type=FeedStockMovement.MovementType.IN,
            delta_kg=quantity_kg,
            moved_by=request.user,
            notes=f"Manual stock input: {quantity_kg}kg",
        )
        messages.success(request, f'Added {quantity_kg}kg to {feed_type.name} stock.')
    else:
        messages.error(request, 'Please provide valid feed stock values.')

    if request.htmx:
        feed_stock_movements = FeedStockMovement.objects.select_related(
            'feed_type', 'moved_by'
        ).order_by('-moved_at')[:50]
        return render(
            request,
            'feed/partials/feed_stock_table.html',
            {'feed_stock_movements': feed_stock_movements}
        )
    return redirect('feed:list')


@login_required
def feed_type_add(request):
    """Add a new feed type using minimal feed data fields."""
    ensure_not_customer(request.user)
    if request.method != 'POST':
        return redirect('feed:list')

    form = FeedTypeForm(request.POST)
    if form.is_valid():
        feed_type = form.save(commit=False)
        feed_type.protein_content = 0
        if feed_type.description is None:
            feed_type.description = ''
        feed_type.save()
        messages.success(request, 'Feed data added successfully.')
    else:
        messages.error(request, 'Please provide valid feed data.')

    if request.htmx:
        feed_types = FeedType.objects.filter(is_active=True).order_by('category', 'name')
        return render(request, 'feed/partials/feed_type_update.html', {
            'feed_types': feed_types,
            'feed_stock_form': FeedStockForm(),
            'feeding_log_form': FeedingLogForm(user=request.user),
        })
    return redirect(request.META.get('HTTP_REFERER', 'feed:list'))


@login_required
def feed_type_edit(request, feed_type_id):
    """Edit an existing feed type."""
    ensure_not_customer(request.user)
    feed_type = get_object_or_404(FeedType, id=feed_type_id)

    if request.method == 'POST':
        form = FeedTypeForm(request.POST, instance=feed_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feed type updated successfully.')
            return redirect(request.META.get('HTTP_REFERER', 'inventory'))
        else:
            messages.error(request, 'Please provide valid feed data.')
    else:
        form = FeedTypeForm(instance=feed_type)
    
    # Normally we would render a specific edit template, but for modal editing we can handle it via JS
    # If the user visits this directly, redirect them back to the list
    return redirect('inventory')


@login_required
def feed_type_delete(request, feed_type_id):
    """Delete a feed type."""
    ensure_not_customer(request.user)
    feed_type = get_object_or_404(FeedType, id=feed_type_id)
    
    if request.method == 'POST':
        if feed_type.feeding_logs.exists() or feed_type.inventory.exists():
            # Instead of deleting, just deactivate to preserve history
            feed_type.is_active = False
            feed_type.save()
            messages.success(request, 'Feed type deactivated (cannot be completely deleted due to existing records).')
        else:
            feed_type.delete()
            messages.success(request, 'Feed type deleted successfully.')
            
    return redirect(request.META.get('HTTP_REFERER', 'inventory'))
