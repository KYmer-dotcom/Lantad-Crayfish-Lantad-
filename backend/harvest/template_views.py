"""
Template views for Harvest module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import HarvestSchedule, HarvestRecord
from fish.models import FishBatch


class HarvestScheduleForm(forms.ModelForm):
    class Meta:
        model = HarvestSchedule
        fields = ['fish_batch', 'scheduled_date', 'estimated_quantity', 'estimated_total_weight', 'target_weight', 'status', 'notes']
        widgets = {
            'fish_batch': forms.Select(attrs={
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
            'estimated_total_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total weight in kg',
                'step': '0.01'
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


class HarvestRecordForm(forms.ModelForm):
    class Meta:
        model = HarvestRecord
        fields = ['fish_batch', 'harvest_schedule', 'harvest_date', 'quantity_harvested', 'total_weight_kg', 'average_weight_per_fish', 'is_partial_harvest', 'notes']
        widgets = {
            'fish_batch': forms.Select(attrs={
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
            'is_partial_harvest': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional notes (optional)'
            }),
        }


@login_required
def harvest_list(request):
    """List all harvest schedules and records"""
    schedules = HarvestSchedule.objects.select_related('fish_batch', 'created_by').all()
    records = HarvestRecord.objects.select_related('fish_batch', 'harvest_schedule', 'harvested_by').all()
    
    context = {
        'schedules': schedules,
        'records': records,
        'schedule_form': HarvestScheduleForm(),
        'record_form': HarvestRecordForm(),
    }
    return render(request, 'harvest/list.html', context)


@login_required
def schedule_create(request):
    """Create a new harvest schedule"""
    if request.method == 'POST':
        form = HarvestScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.created_by = request.user
            schedule.save()
            messages.success(request, f'Harvest schedule for "{schedule.fish_batch.batch_code}" created successfully!')
            
            if request.htmx:
                schedules = HarvestSchedule.objects.select_related('fish_batch', 'created_by').all()
                return render(request, 'harvest/partials/schedules_table.html', {'schedules': schedules})
            
            return redirect('harvest:list')
    else:
        form = HarvestScheduleForm()
    
    if request.htmx:
        return render(request, 'harvest/partials/schedule_form.html', {'form': form})
    
    return redirect('harvest:list')


@login_required
def record_create(request):
    """Create a new harvest record"""
    if request.method == 'POST':
        form = HarvestRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.harvested_by = request.user
            record.save()
            messages.success(request, f'Harvest record for "{record.fish_batch.batch_code}" created successfully!')
            
            if request.htmx:
                records = HarvestRecord.objects.select_related('fish_batch', 'harvest_schedule', 'harvested_by').all()
                return render(request, 'harvest/partials/records_table.html', {'records': records})
            
            return redirect('harvest:list')
    else:
        form = HarvestRecordForm()
    
    if request.htmx:
        return render(request, 'harvest/partials/record_form.html', {'form': form})
    
    return redirect('harvest:list')
