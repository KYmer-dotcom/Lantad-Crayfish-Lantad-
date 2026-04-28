"""
Template views for Fish module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Species, FishBatch
from ponds.models import Pond


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = ['name', 'scientific_name', 'average_growth_rate', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Species name'
            }),
            'scientific_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Scientific name (optional)'
            }),
            'average_growth_rate': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Growth rate (g/day)',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
        }


class FishBatchForm(forms.ModelForm):
    class Meta:
        model = FishBatch
        fields = ['batch_code', 'species', 'pond', 'stocking_date', 'initial_quantity', 
                  'initial_average_weight', 'stage', 'supplier', 'cost_per_unit', 'notes']
        widgets = {
            'batch_code': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Batch code (e.g., BATCH-001)'
            }),
            'species': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pond': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'stocking_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'initial_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Number of fish'
            }),
            'initial_average_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Average weight (g)',
                'step': '0.01'
            }),
            'stage': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'supplier': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Supplier name (optional)'
            }),
            'cost_per_unit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Cost per fish',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Notes (optional)'
            }),
        }


@login_required
def fish_list(request):
    """List all species and fish batches"""
    species = Species.objects.all()
    batches = FishBatch.objects.select_related('species', 'pond').all()
    
    context = {
        'species_list': species,
        'batches': batches,
        'species_form': SpeciesForm(),
        'batch_form': FishBatchForm(),
    }
    return render(request, 'fish/list.html', context)


@login_required
def species_create(request):
    """Create a new species"""
    if request.method == 'POST':
        form = SpeciesForm(request.POST)
        if form.is_valid():
            species = form.save()
            messages.success(request, f'Species "{species.name}" created successfully!')
            
            if request.htmx:
                species_list = Species.objects.all()
                return render(request, 'fish/partials/species_table.html', {'species_list': species_list})
            
            return redirect('fish:list')
    else:
        form = SpeciesForm()
    
    if request.htmx:
        return render(request, 'fish/partials/species_form.html', {'form': form})
    
    return redirect('fish:list')


@login_required
def batch_create(request):
    """Create a new fish batch"""
    if request.method == 'POST':
        form = FishBatchForm(request.POST)
        if form.is_valid():
            batch = form.save(commit=False)
            batch.current_quantity = batch.initial_quantity
            batch.current_average_weight = batch.initial_average_weight
            batch.stocked_by = request.user
            batch.save()
            messages.success(request, f'Batch "{batch.batch_code}" created successfully!')
            
            if request.htmx:
                batches = FishBatch.objects.select_related('species', 'pond').all()
                return render(request, 'fish/partials/batches_table.html', {'batches': batches})
            
            return redirect('fish:list')
    else:
        form = FishBatchForm()
    
    if request.htmx:
        return render(request, 'fish/partials/batch_form.html', {'form': form})
    
    return redirect('fish:list')
