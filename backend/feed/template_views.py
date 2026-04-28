"""
Template views for Feed module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from .models import FeedType, FeedingLog
from fish.models import FishBatch


class FeedTypeForm(forms.ModelForm):
    class Meta:
        model = FeedType
        fields = ['name', 'brand', 'category', 'protein_content', 'price_per_kg', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Feed name'
            }),
            'brand': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Brand (optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'protein_content': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Protein %',
                'step': '0.01'
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Price per kg',
                'step': '0.01'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
        }


class FeedingLogForm(forms.ModelForm):
    class Meta:
        model = FeedingLog
        fields = ['fish_batch', 'feed_type', 'quantity_kg', 'feeding_time', 'notes']
        widgets = {
            'fish_batch': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'feed_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Quantity (kg)',
                'step': '0.01'
            }),
            'feeding_time': forms.DateTimeInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Notes (optional)'
            }),
        }


@login_required
def feed_list(request):
    """List all feed types and feeding logs"""
    feed_types = FeedType.objects.filter(is_active=True)
    feeding_logs = FeedingLog.objects.select_related('fish_batch', 'feed_type', 'fed_by').all()[:50]
    
    context = {
        'feed_types': feed_types,
        'feeding_logs': feeding_logs,
        'feed_type_form': FeedTypeForm(),
        'feeding_log_form': FeedingLogForm(),
    }
    return render(request, 'feed/list.html', context)


@login_required
def feed_type_create(request):
    """Create a new feed type"""
    if request.method == 'POST':
        form = FeedTypeForm(request.POST)
        if form.is_valid():
            feed_type = form.save()
            messages.success(request, f'Feed type "{feed_type.name}" created successfully!')
            
            if request.htmx:
                feed_types = FeedType.objects.filter(is_active=True)
                return render(request, 'feed/partials/feed_types_table.html', {'feed_types': feed_types})
            
            return redirect('feed:list')
    else:
        form = FeedTypeForm()
    
    if request.htmx:
        return render(request, 'feed/partials/feed_type_form.html', {'form': form})
    
    return redirect('feed:list')


@login_required
def feeding_log_create(request):
    """Create a new feeding log"""
    if request.method == 'POST':
        form = FeedingLogForm(request.POST)
        if form.is_valid():
            feeding_log = form.save(commit=False)
            feeding_log.fed_by = request.user
            feeding_log.save()
            messages.success(request, 'Feeding log recorded successfully!')
            
            if request.htmx:
                feeding_logs = FeedingLog.objects.select_related('fish_batch', 'feed_type', 'fed_by').all()[:50]
                return render(request, 'feed/partials/feeding_logs_table.html', {'feeding_logs': feeding_logs})
            
            return redirect('feed:list')
    else:
        form = FeedingLogForm()
    
    if request.htmx:
        return render(request, 'feed/partials/feeding_log_form.html', {'form': form})
    
    return redirect('feed:list')
