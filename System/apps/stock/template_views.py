"""
Template views for Fish module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
from django.shortcuts import get_object_or_404
from django.db.models import ProtectedError
import datetime
from apps.accounts.access import ensure_not_customer, is_owner
from .models import Species, StockBatch, SpeciesStock
from apps.sales.models import Product
from apps.operations.models import Pond


def get_batch_accessible_ponds(user):
    if is_owner(user):
        return Pond.objects.select_related('farm').all()
    return Pond.objects.none()


def filter_batches_for_user(user):
    return StockBatch.objects.select_related('species', 'pond').filter(
        pond__in=get_batch_accessible_ponds(user)
    )


def _build_existing_ponds(user):
    existing_ponds = get_batch_accessible_ponds(user).prefetch_related('species')
    for pond in existing_ponds:
        first_species = pond.species.first()
        pond.default_species_id = first_species.id if first_species else ''
    return existing_ponds


class SpeciesForm(forms.ModelForm):
    class Meta:
        model = Species
        fields = ['name', 'category', 'scientific_name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Species name'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'scientific_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Scientific name (optional)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description (optional)'
            }),
        }


class StockBatchForm(forms.ModelForm):
    class Meta:
        model = StockBatch
        fields = ['species', 'pond', 'initial_quantity']
        widgets = {
            'species': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pond': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'initial_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Quantity to add',
                'min': '1'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['pond'].queryset = get_batch_accessible_ponds(user)

    def clean(self):
        return super().clean()


class SpeciesStockForm(forms.Form):
    species = forms.ModelChoiceField(
        queryset=Species.objects.all(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Quantity to add',
            'min': '1',
        })
    )


class StockBatchUpdateForm(forms.ModelForm):
    class Meta:
        model = StockBatch
        fields = ['current_quantity', 'current_average_weight', 'stage']
        widgets = {
            'current_quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'min': '0'
            }),
            'current_average_weight': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01'
            }),
            'stage': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
        }


@login_required
def products_list(request):
    """Product management for species and pond stock."""
    ensure_not_customer(request.user)
    species = Species.objects.all()
    existing_ponds = _build_existing_ponds(request.user)
    species_stock = SpeciesStock.objects.select_related('species').order_by('species__name')
    products = Product.objects.select_related('species', 'pond').filter(is_active=True)
        
    all_ponds = Pond.objects.all()
            
    for product in products:
        pond_aggregates = {}
        for p in all_ponds:
            if p.product_name == product.name:
                if p.name not in pond_aggregates:
                    pond_aggregates[p.name] = {
                        'name': p.name,
                        'location': p.location or 'All Locations',
                        'capacity': 0,
                        'transfer_date': p.transfer_date
                    }
                qty = p.female_quantity if (p.female_quantity and (p.breeding_type == 'Reproduction' or p.location == 'Breeding Pond')) else p.capacity
                if qty is None:
                    qty = 0
                pond_aggregates[p.name]['capacity'] += qty
                
                # Keep the most recent transfer date
                if p.transfer_date and (not pond_aggregates[p.name]['transfer_date'] or p.transfer_date > pond_aggregates[p.name]['transfer_date']):
                    pond_aggregates[p.name]['transfer_date'] = p.transfer_date

        product.used_in_operations = sorted(list(pond_aggregates.values()), key=lambda x: x['name'])
        product.total_operations_quantity = sum(op['capacity'] for op in product.used_in_operations)
    
    active_batches_count = sum(1 for p in products for op in p.used_in_operations if op['capacity'] > 0)
    total_product_quantity = sum(p.quantity_kg for p in products)
    
    context = {
        'species_list': species,
        'species_stock': species_stock,
        'existing_ponds': existing_ponds,
        'species_form': SpeciesForm(),
        'batch_form': StockBatchForm(user=request.user),
        'species_stock_form': SpeciesStockForm(),
        'products': products,
        'active_batches_count': active_batches_count,
        'total_product_quantity': total_product_quantity,
    }
    return render(request, 'stock_monitoring/list.html', context)


def generate_batch_code():
    today = datetime.date.today()
    prefix = f"BATCH-{today.strftime('%Y%m%d')}-"
    latest = StockBatch.objects.filter(batch_code__startswith=prefix).order_by('-batch_code').first()
    if not latest:
        return f"{prefix}001"

    try:
        next_number = int(latest.batch_code.split('-')[-1]) + 1
    except (ValueError, IndexError):
        next_number = StockBatch.objects.filter(batch_code__startswith=prefix).count() + 1
    return f"{prefix}{next_number:03d}"


@login_required
def species_create(request):
    """Create a new species"""
    ensure_not_customer(request.user)
    if request.method == 'POST':
        form = SpeciesForm(request.POST)
        if form.is_valid():
            species = form.save()
            messages.success(request, f'Species "{species.name}" created successfully!')
            
            if request.htmx:
                species_list = Species.objects.all()
                return render(request, 'stock_monitoring/partials/species_update.html', {
                    'species_list': species_list,
                    'species_stock_form': SpeciesStockForm(),
                    'batch_form': StockBatchForm(user=request.user),
                })
            
            return redirect('stock:list')
    else:
        form = SpeciesForm()
    
    if request.htmx:
        return render(request, 'stock_monitoring/partials/species_form.html', {'form': form})
    
    return redirect('stock:list')


@login_required
def species_edit(request, species_id):
    """Update an existing species."""
    ensure_not_customer(request.user)
    species = get_object_or_404(Species, pk=species_id)
    if request.method == 'POST':
        form = SpeciesForm(request.POST, instance=species)
        if form.is_valid():
            form.save()
            messages.success(request, f'Species "{species.name}" updated successfully!')
            return redirect('stock:list')
    else:
        form = SpeciesForm(instance=species)

    return render(request, 'stock_monitoring/species_form_page.html', {
        'form': form,
        'page_title': f'Edit Species: {species.name}',
        'submit_label': 'Save Changes',
    })


@login_required
def species_delete(request, species_id):
    """Delete species when not used by existing records."""
    ensure_not_customer(request.user)
    species = get_object_or_404(Species, pk=species_id)
    if request.method == 'POST':
        species_name = species.name
        try:
            species.delete()
            messages.success(request, f'Species "{species_name}" removed successfully!')
        except ProtectedError:
            messages.error(request, f'Cannot remove "{species_name}" because it is used by fish batches.')
    return redirect('stock:list')


@login_required
def batch_create(request):
    """Create a new fish batch"""
    ensure_not_customer(request.user)
    if request.method == 'POST':
        form = StockBatchForm(request.POST, user=request.user)
        if form.is_valid():
            pond = form.cleaned_data['pond']
            species = form.cleaned_data['species']
            quantity_to_add = form.cleaned_data['initial_quantity']
            stock_row = SpeciesStock.objects.filter(species=species).first()
            available_stock = stock_row.available_quantity if stock_row else 0
            if quantity_to_add > available_stock:
                messages.error(
                    request,
                    f'Not enough available stock for {species.name}. '
                    f'Available: {available_stock}, Requested: {quantity_to_add}.'
                )
                return redirect('stock:list')
            existing_batch = StockBatch.objects.filter(
                pond=pond,
                species=species,
                is_active=True
            ).order_by('-stocking_date', '-created_at').first()

            if existing_batch:
                previous_qty = existing_batch.current_quantity or 0
                existing_batch.current_quantity = previous_qty + quantity_to_add
                existing_batch.is_active = True
                existing_batch.save(update_fields=['current_quantity', 'current_average_weight', 'stage', 'is_active', 'updated_at'])
                if pond.status == 'empty':
                    pond.status = 'active'
                    pond.save(update_fields=['status'])
                messages.success(request, f'Stock added to existing batch "{existing_batch.batch_code}".')
            else:
                batch = form.save(commit=False)
                batch.batch_code = generate_batch_code()
                batch.current_quantity = batch.initial_quantity
                batch.stocking_date = datetime.date.today()
                batch.initial_average_weight = 0
                batch.current_average_weight = 0
                batch.stage = StockBatch.Stage.FRY
                batch.supplier = ''
                batch.cost_per_unit = 0
                batch.stocked_by = request.user
                batch.save()
                if batch.current_quantity > 0 and batch.pond.status == 'empty':
                    batch.pond.status = 'active'
                    batch.pond.save(update_fields=['status'])
                messages.success(request, f'Batch "{batch.batch_code}" created successfully!')

            stock_row.available_quantity = max(stock_row.available_quantity - quantity_to_add, 0)
            stock_row.save(update_fields=['available_quantity', 'updated_at'])
            
            if request.htmx:
                species_stock = SpeciesStock.objects.select_related('species').order_by('species__name')
                existing_ponds = _build_existing_ponds(request.user)
                return render(request, 'stock_monitoring/partials/stock_update.html', {
                    'species_stock': species_stock,
                    'existing_ponds': existing_ponds,
                })
            
            return redirect('stock:list')
    else:
        form = StockBatchForm(user=request.user)
    
    if request.htmx:
        return render(request, 'stock_monitoring/partials/batch_form.html', {'form': form})
    
    return redirect('stock:list')


@login_required
def species_stock_add(request):
    """Add available fish stock for a species."""
    ensure_not_customer(request.user)
    if request.method != 'POST':
        return redirect('stock:list')

    form = SpeciesStockForm(request.POST)
    if form.is_valid():
        species = form.cleaned_data['species']
        quantity = form.cleaned_data['quantity']
        stock_row, _ = SpeciesStock.objects.get_or_create(
            species=species,
            defaults={'available_quantity': 0}
        )
        stock_row.available_quantity += quantity
        stock_row.save(update_fields=['available_quantity', 'updated_at'])
        messages.success(request, f'Added {quantity} to {species.name} stock.')
    else:
        messages.error(request, 'Please provide a valid species and quantity.')

    if request.htmx:
        species_stock = SpeciesStock.objects.select_related('species').order_by('species__name')
        return render(request, 'stock_monitoring/partials/species_stock_table.html', {'species_stock': species_stock})
    return redirect('stock:list')


@login_required
def batch_update(request, batch_id):
    """Update fish stock quantities for an existing batch."""
    ensure_not_customer(request.user)
    batch = get_object_or_404(filter_batches_for_user(request.user), pk=batch_id)
    if request.method != 'POST':
        return redirect('stock:list')

    form = StockBatchUpdateForm(request.POST, instance=batch)
    if form.is_valid():
        updated_batch = form.save(commit=False)
        if updated_batch.current_quantity <= 0:
            updated_batch.current_quantity = 0
            updated_batch.is_active = False
            if updated_batch.pond.status != 'empty':
                updated_batch.pond.status = 'empty'
                updated_batch.pond.save(update_fields=['status'])
        else:
            updated_batch.is_active = True
            if updated_batch.pond.status == 'empty':
                updated_batch.pond.status = 'active'
                updated_batch.pond.save(update_fields=['status'])

        updated_batch.save(update_fields=['current_quantity', 'current_average_weight', 'stage', 'is_active', 'updated_at'])
        messages.success(request, f'Batch "{updated_batch.batch_code}" stock updated successfully!')
    else:
        messages.error(request, 'Please provide valid stock values.')

    return redirect('stock:list')
