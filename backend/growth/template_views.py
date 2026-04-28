"""
Template views for Growth module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import GrowthSample, MortalityRecord
from fish.models import FishBatch


class GrowthSampleForm(forms.ModelForm):
    class Meta:
        model = GrowthSample
        fields = ['fish_batch', 'sample_date', 'sample_size', 'average_weight', 'min_weight', 'max_weight', 'average_length', 'notes']
        widgets = {
            'fish_batch': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'sample_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'sample_size': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Number of fish sampled'
            }),
            'average_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Average weight (g)',
                'step': '0.01'
            }),
            'min_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Min weight (g)',
                'step': '0.01'
            }),
            'max_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Max weight (g)',
                'step': '0.01'
            }),
            'average_length': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Average length (cm)',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Notes (optional)'
            }),
        }


class MortalityRecordForm(forms.ModelForm):
    class Meta:
        model = MortalityRecord
        fields = ['fish_batch', 'record_date', 'quantity', 'cause', 'estimated_weight_loss', 'notes']
        widgets = {
            'fish_batch': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'record_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Number of fish died'
            }),
            'cause': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'estimated_weight_loss': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Est. weight loss (g)',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Notes (optional)'
            }),
        }


@login_required
def growth_list(request):
    """List all growth samples and mortality records"""
    samples = GrowthSample.objects.select_related('fish_batch', 'sampled_by').all()
    mortality_records = MortalityRecord.objects.select_related('fish_batch', 'recorded_by').all()
    
    # Prepare chart data - growth trend over time
    chart_data = list(
        GrowthSample.objects
        .order_by('sample_date')
        .values('sample_date', 'average_weight')[:50]
    )
    chart_labels = [str(d['sample_date']) for d in chart_data]
    chart_values = [float(d['average_weight']) for d in chart_data]
    
    context = {
        'samples': samples,
        'mortality_records': mortality_records,
        'sample_form': GrowthSampleForm(),
        'mortality_form': MortalityRecordForm(),
        'chart_labels': chart_labels,
        'chart_values': chart_values,
    }
    return render(request, 'growth/list.html', context)


@login_required
def sample_create(request):
    """Create a new growth sample"""
    if request.method == 'POST':
        form = GrowthSampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            sample.sampled_by = request.user
            sample.save()
            messages.success(request, f'Growth sample recorded for {sample.fish_batch.batch_code}!')
            
            if request.htmx:
                samples = GrowthSample.objects.select_related('fish_batch', 'sampled_by').all()
                return render(request, 'growth/partials/samples_table.html', {'samples': samples})
            
            return redirect('growth:list')
    else:
        form = GrowthSampleForm()
    
    if request.htmx:
        return render(request, 'growth/partials/sample_form.html', {'form': form})
    
    return redirect('growth:list')


@login_required
def mortality_create(request):
    """Create a new mortality record"""
    if request.method == 'POST':
        form = MortalityRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.recorded_by = request.user
            record.save()
            messages.success(request, f'Mortality record created for {record.fish_batch.batch_code}!')
            
            if request.htmx:
                mortality_records = MortalityRecord.objects.select_related('fish_batch', 'recorded_by').all()
                return render(request, 'growth/partials/mortality_table.html', {'mortality_records': mortality_records})
            
            return redirect('growth:list')
    else:
        form = MortalityRecordForm()
    
    if request.htmx:
        return render(request, 'growth/partials/mortality_form.html', {'form': form})
    
    return redirect('growth:list')
