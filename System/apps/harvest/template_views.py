"""
Template views for Harvest module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms

from apps.accounts.access import filter_by_pond, ensure_not_customer
from .models import HarvestSchedule, HarvestRecord
from apps.stock.models import StockBatch


class HarvestScheduleForm(forms.ModelForm):
    class Meta:
        model = HarvestSchedule
        fields = ['stock_batch', 'scheduled_date', 'estimated_quantity', 'target_weight', 'status', 'notes']
        widgets = {
            'stock_batch': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'estimated_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Number of fish'
            }),
            'target_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Target weight per fish (g)',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['stock_batch'].queryset = filter_by_pond(
                user,
                StockBatch.objects.select_related('pond', 'species'),
                'pond'
            )


class HarvestRecordForm(forms.ModelForm):
    class Meta:
        model = HarvestRecord
        fields = [
            'stock_batch', 'harvest_schedule', 'harvest_date', 'quantity_harvested',
            'total_weight_kg', 'average_weight_per_fish', 'grade_a_quantity',
            'grade_b_quantity', 'grade_c_quantity', 'is_partial_harvest', 'notes'
        ]
        widgets = {
            'stock_batch': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'harvest_schedule': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'harvest_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'quantity_harvested': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Number of fish harvested'
            }),
            'total_weight_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total weight in kg',
                'step': '0.01'
            }),
            'average_weight_per_fish': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Average weight per fish (g)',
                'step': '0.01'
            }),
            'grade_a_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Grade A',
                'min': '0'
            }),
            'grade_b_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Grade B',
                'min': '0'
            }),
            'grade_c_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Grade C',
                'min': '0'
            }),
            'is_partial_harvest': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['stock_batch'].queryset = filter_by_pond(
                user,
                StockBatch.objects.select_related('pond', 'species'),
                'pond'
            )

    def clean(self):
        cleaned_data = super().clean()
        quantity_harvested = cleaned_data.get('quantity_harvested') or 0
        grade_a = cleaned_data.get('grade_a_quantity') or 0
        grade_b = cleaned_data.get('grade_b_quantity') or 0
        grade_c = cleaned_data.get('grade_c_quantity') or 0
        graded_total = grade_a + grade_b + grade_c

        if graded_total > quantity_harvested:
            self.add_error(
                'grade_c_quantity',
                'Total graded quantity cannot exceed harvested quantity.'
            )
        return cleaned_data


@login_required
def harvest_list(request):
    """List all harvest schedules and records"""
    ensure_not_customer(request.user)
    from apps.operations.models import Pond
    from apps.accounts.access import get_accessible_ponds
    all_ponds = get_accessible_ponds(request.user)
    main_ponds = all_ponds.filter(location='Main Pond')
    breeding_ponds = all_ponds.filter(location='Breeding Pond')
    azula_ponds = all_ponds.filter(location='Azula')
    from django.db.models import Case, When, Value, IntegerField
    sw_ponds = all_ponds.filter(location='Superworm Cabin').annotate(
        shelf_order=Case(
            When(shelf_position__startswith='Left', then=Value(1)),
            When(shelf_position__startswith='Right', then=Value(2)),
            When(shelf_position__startswith='Back', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('shelf_order', 'shelf_position')
    from django.db.models import Q
    records_qs = HarvestRecord.objects.select_related('stock_batch', 'harvest_schedule', 'harvested_by').filter(
        Q(stock_batch__pond__location='Main Pond') | Q(stock_batch__pond__breeding_type='Crilings')
    )
    records = filter_by_pond(
        request.user,
        records_qs,
        'stock_batch__pond'
    )
    
    sw_records_qs = HarvestRecord.objects.select_related('stock_batch', 'harvest_schedule', 'harvested_by').filter(
        stock_batch__pond__location='Superworm Cabin'
    )
    sw_records = filter_by_pond(
        request.user,
        sw_records_qs,
        'stock_batch__pond'
    )
    
    from django.db.models import Sum
    total_yield = (records.aggregate(Sum('total_weight_kg'))['total_weight_kg__sum'] or 0) + (sw_records.aggregate(Sum('total_weight_kg'))['total_weight_kg__sum'] or 0)
    
    import json
    from datetime import timedelta
    harvest_events = []
    
    for pond in main_ponds:
        if pond.transfer_date:
            start = pond.transfer_date + timedelta(days=150)
            end = pond.transfer_date + timedelta(days=180)
            harvest_events.append({
                'start': start.strftime('%Y-%m-%d'),
                'end': end.strftime('%Y-%m-%d'),
                'pond': f"{pond.name} (Main)"
            })
            
    for pond in sw_ponds:
        if pond.transfer_date:
            start = pond.transfer_date + timedelta(days=90)
            end = pond.transfer_date + timedelta(days=120)
            harvest_events.append({
                'start': start.strftime('%Y-%m-%d'),
                'end': end.strftime('%Y-%m-%d'),
                'pond': f"{pond.name} (Superworm)"
            })
            
    for pond in breeding_ponds:
        if pond.transfer_date:
            if pond.breeding_type == 'Reproduction':
                est_date = pond.transfer_date + timedelta(days=21)
                harvest_events.append({
                    'start': est_date.strftime('%Y-%m-%d'),
                    'end': est_date.strftime('%Y-%m-%d'),
                    'pond': f"{pond.name} (Breeding)"
                })
            elif pond.breeding_type == 'Crilings':
                est_date = pond.transfer_date + timedelta(days=60)
                harvest_events.append({
                    'start': est_date.strftime('%Y-%m-%d'),
                    'end': est_date.strftime('%Y-%m-%d'),
                    'pond': f"{pond.name} (Breeding)"
                })
                
    for pond in azula_ponds:
        if pond.transfer_date:
            est_date = pond.transfer_date + timedelta(days=30)
            harvest_events.append({
                'start': est_date.strftime('%Y-%m-%d'),
                'end': est_date.strftime('%Y-%m-%d'),
                'pond': f"{pond.name} (Azula)"
            })
            
    transfers_count = len(breeding_ponds)
    estimated_harvest_count = len(main_ponds) + len(sw_ponds) + len(azula_ponds)

    context = {
        'harvest_events': harvest_events,
        'main_ponds': main_ponds,
        'breeding_ponds': breeding_ponds,
        'sw_ponds': sw_ponds,
        'azula_ponds': azula_ponds,
        'records': records,
        'sw_records': sw_records,
        'total_schedules': len(main_ponds) + len(breeding_ponds) + len(sw_ponds) + len(azula_ponds),
        'transfers_count': transfers_count,
        'estimated_harvest_count': estimated_harvest_count,
        'total_records': len(records) + len(sw_records),
        'total_yield': total_yield,
        'schedule_form': HarvestScheduleForm(user=request.user),
        'record_form': HarvestRecordForm(user=request.user),
    }
    return render(request, 'harvest_management/list.html', context)


@login_required
def schedule_create(request):
    """Create a new harvest schedule"""
    ensure_not_customer(request.user)
    if request.method == 'POST':
        form = HarvestScheduleForm(request.POST, user=request.user)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.created_by = request.user
            schedule.estimated_total_weight = (
                (schedule.estimated_quantity * schedule.target_weight) / 1000
                if schedule.estimated_quantity and schedule.target_weight else 0
            )
            schedule.save()
            messages.success(request, f'Harvest schedule for "{schedule.stock_batch.batch_code}" created successfully!')
            
            if request.htmx:
                schedules = filter_by_pond(
                    request.user,
                    HarvestSchedule.objects.select_related('stock_batch', 'created_by'),
                    'stock_batch__pond'
                )
                return render(request, 'harvest_management/partials/schedules_table.html', {'schedules': schedules})
            
            return redirect('harvest:list')
    else:
        form = HarvestScheduleForm(user=request.user)
    
    if request.htmx:
        return render(request, 'harvest_management/partials/schedule_form.html', {'form': form})
    
    return redirect('harvest:list')


@login_required
def record_create(request):
    """Create a new harvest record"""
    ensure_not_customer(request.user)
    if request.method == 'POST':
        form = HarvestRecordForm(request.POST, user=request.user)
        if form.is_valid():
            record = form.save(commit=False)
            batch = record.stock_batch
            if record.quantity_harvested > batch.current_quantity:
                messages.error(
                    request,
                    f'Cannot harvest {record.quantity_harvested} fish from {batch.batch_code}. '
                    f'Available: {batch.current_quantity}.'
                )
                return redirect('harvest:list')
            record.harvested_by = request.user
            record.save()
            batch.current_quantity -= record.quantity_harvested
            if batch.current_quantity <= 0:
                batch.current_quantity = 0
                batch.is_active = False
                batch.pond.status = 'empty'
                batch.pond.save(update_fields=['status'])
            batch.save(update_fields=['current_quantity', 'is_active', 'updated_at'])
            messages.success(request, f'Harvest record for "{record.stock_batch.batch_code}" created successfully!')
            
            if request.htmx:
                records = filter_by_pond(
                    request.user,
                    HarvestRecord.objects.select_related('stock_batch', 'harvest_schedule', 'harvested_by'),
                    'stock_batch__pond'
                )
                return render(request, 'harvest_management/partials/records_table.html', {'records': records})
            
            return redirect('harvest:list')
    else:
        form = HarvestRecordForm(user=request.user)
    
    if request.htmx:
        return render(request, 'harvest_management/partials/record_form.html', {'form': form})
    
    return redirect('harvest:list')
