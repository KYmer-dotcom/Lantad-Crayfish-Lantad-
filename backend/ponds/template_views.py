"""
Template views for Ponds module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import Farm, Pond


class FarmForm(forms.ModelForm):
    class Meta:
        model = Farm
        fields = ['name', 'location', 'total_area', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Farm name'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Location'
            }),
            'total_area': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Total area (m²)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
        }


class PondForm(forms.ModelForm):
    class Meta:
        model = Pond
        fields = ['farm', 'name', 'size', 'depth', 'capacity']
        widgets = {
            'farm': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Pond name'
            }),
            'size': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Size (m²)'
            }),
            'depth': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Depth (m)',
                'step': '0.01'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Fish capacity'
            }),
        }


@login_required
def ponds_list(request):
    """List all farms and ponds"""
    farms = Farm.objects.all()
    ponds = Pond.objects.select_related('farm').all()
    
    context = {
        'farms': farms,
        'ponds': ponds,
        'farm_form': FarmForm(),
        'pond_form': PondForm(),
    }
    return render(request, 'ponds/list.html', context)


@login_required
def farm_create(request):
    """Create a new farm"""
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.owner = request.user
            farm.save()
            messages.success(request, f'Farm "{farm.name}" created successfully!')
            
            if request.htmx:
                # Return updated farms table
                farms = Farm.objects.all()
                return render(request, 'ponds/partials/farms_table.html', {'farms': farms})
            
            return redirect('ponds:list')
    else:
        form = FarmForm()
    
    if request.htmx:
        return render(request, 'ponds/partials/farm_form.html', {'form': form})
    
    return redirect('ponds:list')


@login_required
def pond_create(request):
    """Create a new pond"""
    if request.method == 'POST':
        form = PondForm(request.POST)
        if form.is_valid():
            pond = form.save()
            messages.success(request, f'Pond "{pond.name}" created successfully!')
            
            if request.htmx:
                ponds = Pond.objects.select_related('farm').all()
                return render(request, 'ponds/partials/ponds_table.html', {'ponds': ponds})
            
            return redirect('ponds:list')
    else:
        form = PondForm()
    
    if request.htmx:
        return render(request, 'ponds/partials/pond_form.html', {'form': form})
    
    return redirect('ponds:list')
