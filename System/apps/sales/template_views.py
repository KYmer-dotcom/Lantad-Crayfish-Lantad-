"""
Template views for Sales module
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Sum, Count, Q, Case, When, Value, IntegerField, Prefetch, F
from django.core.paginator import Paginator
from django import forms
from decimal import Decimal
import datetime
import re
from apps.accounts.access import is_customer, get_customer_profile, is_owner, is_rider, get_rider_profile, get_accessible_ponds
from apps.accounts.models import User
from .models import Customer, Product, SalesOrder, Delivery, Rider, PaymentSetting



GUEST_CUSTOMER_SESSION_KEY = 'guest_customer_profile'
WHOLESALE_MIN_QTY_KG = Decimal('50')


def _ensure_sales_owner(request):
    if is_customer(request.user):
        return redirect('sales:customer_portal')
    if is_rider(request.user):
        return redirect('sales:rider_portal')
    if not is_owner(request.user):
        messages.error(request, 'Only owner accounts can access this section.')
        return redirect('dashboard')
    return None


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'customer_type', 'contact_person', 'phone', 'email', 'address', 'credit_limit', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Customer name'
            }),
            'customer_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Contact person (optional)'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Phone number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Email (optional)'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Address'
            }),
            'credit_limit': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Credit limit (₱)',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Notes (optional)'
            }),
        }


class SalesOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['customer', 'product', 'order_type', 'order_date', 'quantity_kg', 'price_per_kg', 'discount',
                  'status', 'payment_status', 'delivery_address', 'notes']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'order_customer'
            }),
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'order_product'
            }),
            'order_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'order_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Quantity (kg)',
                'step': '0.01',
                'id': 'order_quantity',
                'oninput': 'calculateTotal()'
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Price per kg (₱)',
                'step': '0.01',
                'id': 'order_price',
                'oninput': 'calculateTotal()'
            }),
            'discount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Discount (₱)',
                'step': '0.01',
                'id': 'order_discount',
                'oninput': 'calculateTotal()'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'payment_status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Delivery address (optional)'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Notes (optional)'
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)


def generate_order_number():
    """Generate unique order number"""
    today = datetime.date.today()
    prefix = f"SO-{today.strftime('%Y%m%d')}"
    count = SalesOrder.objects.filter(order_number__startswith=prefix).count() + 1
    return f"{prefix}-{count:04d}"


def _resolve_customer_profile(request):
    if request.user.is_authenticated and is_customer(request.user):
        customer = get_customer_profile(request.user)
        if customer:
            return customer, False
    return None, True


@login_required
def sales_list(request):
    """List all customers and sales orders with summary stats"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    all_orders = SalesOrder.objects.select_related('customer', 'product').all()
    
    # Auto-create Delivery records for any existing delivery SalesOrders that don't have one
    delivery_orders = all_orders.exclude(delivery_address__iexact='pickup').filter(deliveries__isnull=True)
    for ord_obj in delivery_orders:
        if ord_obj.status in [SalesOrder.Status.DELIVERED, SalesOrder.Status.COMPLETED]:
            deliv_status = Delivery.Status.DELIVERED
            deliv_date = ord_obj.order_date
        elif ord_obj.status == SalesOrder.Status.CANCELLED:
            deliv_status = Delivery.Status.CANCELLED
            deliv_date = None
        elif ord_obj.status == SalesOrder.Status.SHIPPED:
            deliv_status = Delivery.Status.IN_TRANSIT
            deliv_date = None
        else:
            deliv_status = Delivery.Status.SCHEDULED
            deliv_date = None

        Delivery.objects.create(
            order=ord_obj,
            scheduled_date=ord_obj.order_date,
            delivered_date=deliv_date,
            delivery_location=ord_obj.delivery_address or "Standard Delivery",
            quantity_kg=ord_obj.quantity_kg,
            status=deliv_status,
            created_by=ord_obj.created_by
        )
        
    products = Product.objects.filter(is_active=True).select_related('species', 'pond')
    deliveries = Delivery.objects.select_related('order', 'created_by').all()
    active_orders_prefetch = Prefetch(
        'orders',
        queryset=SalesOrder.objects.exclude(status__in=['completed', 'cancelled']).select_related('product')
    )
    customers = Customer.objects.filter(orders__status__in=['pending', 'confirmed', 'processing', 'shipped', 'delivered']).annotate(
        active_total=Sum('orders__total_amount', filter=Q(orders__status__in=['pending', 'confirmed', 'processing', 'shipped', 'delivered']))
    ).prefetch_related(active_orders_prefetch).distinct().order_by('name')

    
    # Summary stats
    total_orders = all_orders.exclude(status='cancelled').count()
    total_revenue = all_orders.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    pending_orders = all_orders.exclude(status__in=['completed', 'cancelled']).count()
    
    # Filter to show only Pickup orders in the "Pick up Orders" list
    pickup_orders = all_orders.filter(delivery_address__iexact='pickup')
    
    context = {
        'orders': pickup_orders,
        'all_orders': all_orders.filter(status='completed').order_by('-order_date', '-id'),
        'products': products,
        'deliveries': deliveries,
        'customers': customers,
        'product_form': ProductForm(user=request.user),
        'order_form': SalesOrderForm(user=request.user, initial={'order_date': datetime.date.today(), 'discount': 0}),
        'delivery_form': DeliveryForm(user=request.user),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
    }
    return render(request, 'sales_management/list.html', context)


@login_required
def sales_orders_page(request):
    """Dedicated admin page for active orders management."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    all_orders = SalesOrder.objects.select_related('customer', 'product').all()
    active_orders_prefetch = Prefetch(
        'orders',
        queryset=SalesOrder.objects.exclude(status__in=['completed', 'cancelled']).select_related('product')
    )
    customers = Customer.objects.filter(orders__status__in=['pending', 'confirmed', 'processing', 'shipped', 'delivered']).annotate(
        active_total=Sum('orders__total_amount', filter=Q(orders__status__in=['pending', 'confirmed', 'processing', 'shipped', 'delivered']))
    ).prefetch_related(active_orders_prefetch).distinct().order_by('name')

    total_active_orders = all_orders.exclude(status__in=['completed', 'cancelled']).count()
    pending_orders = all_orders.filter(status='pending').count()
    total_active_revenue = all_orders.exclude(status__in=['completed', 'cancelled']).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    from apps.sales.models import PaymentSetting
    payment_settings = PaymentSetting.get_settings()

    context = {
        'customers': customers,
        'total_orders': total_active_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_active_revenue,
        'payment_settings': payment_settings,
    }
    return render(request, 'sales_management/orders.html', context)


@login_required
def payment_settings_update(request):
    """Update owner GCash payment destination and payment settings."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    if request.method == 'POST':
        from apps.sales.models import PaymentSetting
        settings_obj = PaymentSetting.get_settings()
        settings_obj.gcash_name = request.POST.get('gcash_name', '').strip() or "SILAY SUPERWORM & CRAYFISH"
        settings_obj.gcash_number = request.POST.get('gcash_number', '').strip() or "09171234567"
        settings_obj.is_gcash_enabled = (request.POST.get('is_gcash_enabled') == 'on' or request.POST.get('is_gcash_enabled') == 'true')
        settings_obj.is_cod_enabled = (request.POST.get('is_cod_enabled') == 'on' or request.POST.get('is_cod_enabled') == 'true')

        if 'gcash_qr_image' in request.FILES:
            settings_obj.gcash_qr_image = request.FILES['gcash_qr_image']

        settings_obj.save()
        messages.success(request, f'Payment settings saved! GCash payments will now be routed to {settings_obj.gcash_number}.')

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'gcash_number': settings_obj.gcash_number, 'gcash_name': settings_obj.gcash_name})

    return redirect('sales:orders_admin')



@login_required
def order_edit_admin(request, order_id):
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    order = get_object_or_404(
        SalesOrder.objects.filter(Q(created_by__isnull=True) | Q(created_by__role=User.Role.CUSTOMER)),
        pk=order_id,
    )
    if request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=order, user=request.user)
        if form.is_valid():
            updated_order = form.save(commit=False)
            updated_order.total_amount = (
                (updated_order.quantity_kg * updated_order.price_per_kg) - updated_order.discount
            )
            updated_order.save()
            messages.success(request, f'Order "{updated_order.order_number}" updated successfully.')
            return redirect('sales:orders_admin')
    else:
        form = SalesOrderForm(instance=order, user=request.user)

    return render(request, 'sales_management/order_form_page.html', {
        'form': form,
        'page_title': f'Edit Order {order.order_number}',
        'submit_label': 'Save Changes',
    })


@login_required
def order_delete_admin(request, order_id):
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    order = get_object_or_404(
        SalesOrder.objects.filter(Q(created_by__isnull=True) | Q(created_by__role=User.Role.CUSTOMER)),
        pk=order_id,
    )
    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Order "{order_number}" deleted successfully.')
    return redirect('sales:orders_admin')


@login_required
def order_delete(request, order_id):
    """Delete a sales order from any page and redirect back"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    order = get_object_or_404(SalesOrder, pk=order_id)
    if request.method == 'POST':
        order_number = order.order_number
        order.delete()
        messages.success(request, f'Order "{order_number}" deleted successfully.')
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('sales:list')


@login_required
def customer_create(request):
    """Create a new customer"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" created successfully!')
            
            if request.htmx:
                customers = Customer.objects.filter(is_active=True).annotate(
                    total_purchases_amount=Sum('orders__total_amount', filter=Q(orders__status='completed'))
                )
                return render(request, 'sales_management/partials/customers_table.html', {'customers': customers})
            
            return redirect('sales:list')
    else:
        form = CustomerForm()
    
    if request.htmx:
        return render(request, 'sales_management/partials/customer_form.html', {'form': form})
    
    return redirect('sales:list')


@login_required
def customer_delete(request, customer_id):
    """Delete a customer"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        name = customer.name
        customer.delete()
        messages.success(request, f'Customer "{name}" deleted successfully!')
    return redirect('sales:list')


@login_required
def order_create(request):
    """Create a new sales order"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    if request.method == 'POST':
        form = SalesOrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_number = generate_order_number()
            order.total_amount = (order.quantity_kg * order.price_per_kg) - order.discount
            order.created_by = request.user
            order.save()
            
            if order.delivery_address and order.delivery_address.lower() != 'pickup':
                Delivery.objects.create(
                    order=order,
                    scheduled_date=order.order_date,
                    delivery_location=order.delivery_address,
                    quantity_kg=order.quantity_kg,
                    created_by=request.user
                )
                
            messages.success(request, f'Order "{order.order_number}" created successfully!')
            
            if request.htmx:
                orders = SalesOrder.objects.select_related('customer', 'product').all()
            
            return redirect('sales:list')
    else:
        form = SalesOrderForm(user=request.user)
    
    if request.htmx:
        return render(request, 'sales_management/partials/order_form.html', {'form': form})
    
    return redirect('sales:list')


@login_required
def order_status_update(request, order_id):
    """Update order status"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    order = get_object_or_404(SalesOrder, pk=order_id)

    if request.method == 'POST':
        status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in SalesOrder.Status.choices]
        if status in valid_statuses:
            order.status = status
            if status in [SalesOrder.Status.DELIVERED, SalesOrder.Status.COMPLETED] and not order.delivery_date:
                order.delivery_date = datetime.date.today()
            order.save()
            messages.success(request, f'Order "{order.order_number}" updated successfully!')

        if request.htmx:
            orders = SalesOrder.objects.select_related('customer', 'product').all()

    return redirect('sales:list')


@login_required
def order_payment_update(request, order_id):
    """Update order payment status and receipt image"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    order = get_object_or_404(SalesOrder, pk=order_id)

    if request.method == 'POST':
        payment_status = request.POST.get('payment_status')
        valid_statuses = [choice[0] for choice in SalesOrder.PaymentStatus.choices]
        if payment_status in valid_statuses:
            order.payment_status = payment_status
            if payment_status == 'paid':
                order.status = SalesOrder.Status.COMPLETED

        if 'receipt_image' in request.FILES:
            order.receipt_image = request.FILES['receipt_image'].read()

        order.save()
        messages.success(request, f'Payment status for order "{order.order_number}" updated successfully!')

    return redirect('sales:list')


@login_required
def order_receipt_view(request, order_id):
    """Serve the raw bytea receipt image from the database"""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    order = get_object_or_404(SalesOrder, pk=order_id)
    if order.receipt_image:
        from django.http import HttpResponse
        img_data = bytes(order.receipt_image)
        return HttpResponse(img_data, content_type='image/jpeg')
    from django.http import Http404
    raise Http404("No receipt image found")


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'species', 'pond', 'category', 'accent_color', 'icon', 'quantity_kg', 'reorder_level_kg', 'unit_price', 'price_per_kg', 'pieces_per_kg', 'is_active', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Product name'
            }),
            'species': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'pond': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01'
            }),
            'reorder_level_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Price per pc'
            }),
            'price_per_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Price per kg'
            }),
            'pieces_per_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Pieces per kg'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['pond'].queryset = get_accessible_ponds(user)


class RiderForm(forms.ModelForm):
    class Meta:
        model = Rider
        fields = ['name', 'phone', 'vehicle_type', 'plate_number', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Rider full name',
                'autocomplete': 'off'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g. 09123456789',
                'maxlength': '11',
                'inputmode': 'numeric',
                'pattern': '[0-9]{11}',
                'oninput': "this.value = this.value.replace(/[^0-9]/g, '').slice(0, 11);",
                'autocomplete': 'off'
            }),
            'vehicle_type': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'e.g. Motorcycle, Tricycle, Delivery Van',
                'autocomplete': 'off'
            }),
            'plate_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent uppercase',
                'placeholder': 'Plate / Vehicle ID',
                'style': 'text-transform: uppercase;',
                'oninput': 'this.value = this.value.toUpperCase();',
                'autocomplete': 'off'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Additional rider notes...'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '')
        digits = re.sub(r'\D', '', phone)
        if len(digits) > 11:
            digits = digits[:11]
        if len(digits) != 11:
            raise forms.ValidationError('Phone number must be 11 digits (e.g. 09123456789).')
        return digits

    def clean_plate_number(self):
        plate = self.cleaned_data.get('plate_number', '')
        return plate.strip().upper()


class DeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['order', 'rider', 'scheduled_date', 'delivered_date', 'delivery_location', 'quantity_kg', 'status', 'notes']
        widgets = {
            'order': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'rider': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'scheduled_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'delivered_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'delivery_location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Delivery location'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['rider'].queryset = Rider.objects.filter(is_active=True).order_by('name')
        self.fields['rider'].required = False


class CustomerOrderForm(forms.ModelForm):
    class Meta:
        model = SalesOrder
        fields = ['product', 'quantity_kg', 'delivery_address', 'notes']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'quantity_kg': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2,
                'placeholder': 'Delivery address'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        products = Product.objects.filter(is_active=True, quantity_kg__gt=0).select_related('species')
        self.fields['product'].queryset = products
        self.fields['product'].label_from_instance = (
            lambda product: (
                f"{product.name} | {product.get_category_display()} | "
                f"{product.species.name if product.species else 'Unspecified species'} | "
                f"{product.quantity_kg:.2f} kg available"
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity_kg')
        if product and quantity:
            if quantity <= 0:
                self.add_error('quantity_kg', 'Quantity must be greater than zero.')
            elif quantity > product.quantity_kg:
                self.add_error('quantity_kg', f'Only {product.quantity_kg:.2f} kg is available for this product.')
        return cleaned_data


class CustomerLocationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['map_latitude', 'map_longitude']
        widgets = {
            'map_latitude': forms.NumberInput(attrs={
                'class': 'w-full rounded-md border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm text-gray-900',
                'readonly': 'readonly',
                'step': '0.000001',
            }),
            'map_longitude': forms.NumberInput(attrs={
                'class': 'w-full rounded-md border border-yellow-200 bg-yellow-50 px-3 py-2 text-sm text-gray-900',
                'readonly': 'readonly',
                'step': '0.000001',
            }),
        }


@login_required
def product_create(request):
    if is_customer(request.user):
        return redirect('sales:customer_portal')
    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        data = request.POST.copy()
        data['category'] = data.get('category') or Product.Category.FISH
        data['accent_color'] = data.get('accent') or 'indigo'
        data['icon'] = data.get('icon') or 'fish'
        data['quantity_kg'] = data.get('quantity_kg') or '0'
        data['reorder_level_kg'] = data.get('reorder_level_kg') or '0'
        data['unit_price'] = data.get('unit_price') or '0'
        data['price_per_kg'] = data.get('price_per_kg') or '0'
        data['pieces_per_kg'] = data.get('pieces_per_kg') or '1'
        if 'is_active' not in data:
            data['is_active'] = 'on'
        # Ensure format adherence
        data['quantity_kg'] = f"{float(data['quantity_kg']):.2f}" if data['quantity_kg'] else '0.00'
        data['unit_price'] = f"{float(data['unit_price']):.2f}" if data['unit_price'] else '0.00'
        data['price_per_kg'] = f"{float(data['price_per_kg']):.2f}" if data['price_per_kg'] else '0.00'
        data['pieces_per_kg'] = f"{float(data['pieces_per_kg']):.2f}" if data['pieces_per_kg'] else '1.00'
        form = ProductForm(data, user=request.user)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" created successfully!')

            if request.htmx:
                products = Product.objects.filter(is_active=True).select_related('species', 'pond')

            return redirect(next_url or 'sales:list')
        messages.error(request, 'Product creation failed. Check required fields.')
    else:
        form = ProductForm(user=request.user)

    if request.htmx:
        return render(request, 'sales_management/partials/product_form.html', {'form': form})

    return redirect(next_url or 'sales:list')


@login_required
def product_delete(request, product_id):
    if is_customer(request.user):
        return redirect('sales:customer_portal')
    if request.method != 'POST':
        return redirect('sales:list')

    product = get_object_or_404(Product, pk=product_id)

    product.is_active = False
    product.save(update_fields=['is_active'])
    messages.success(request, f'Product "{product.name}" removed successfully.')

    next_url = request.POST.get('next') or request.GET.get('next')
    return redirect(next_url or 'sales:list')


@login_required
def product_edit(request, product_id):
    if is_customer(request.user):
        return redirect('sales:customer_portal')
        
    product = get_object_or_404(Product, pk=product_id)

    next_url = request.POST.get('next') or request.GET.get('next')
    if request.method == 'POST':
        name = request.POST.get('name')
        notes = request.POST.get('notes')
        accent = request.POST.get('accent')
        icon = request.POST.get('icon')
        unit_price = request.POST.get('unit_price')
        price_per_kg = request.POST.get('price_per_kg')
        pieces_per_kg = request.POST.get('pieces_per_kg')
        quantity_kg = request.POST.get('quantity_kg')
        
        if name:
            product.name = name
            if notes is not None:
                product.notes = notes
            if accent:
                product.accent_color = accent
            if icon:
                product.icon = icon
            
            if unit_price:
                try:
                    product.unit_price = f"{float(unit_price):.2f}"
                except ValueError:
                    pass
            if price_per_kg:
                try:
                    product.price_per_kg = f"{float(price_per_kg):.2f}"
                except ValueError:
                    pass
            if pieces_per_kg:
                try:
                    product.pieces_per_kg = f"{float(pieces_per_kg):.2f}"
                except ValueError:
                    pass
            if quantity_kg:
                try:
                    product.quantity_kg = f"{float(quantity_kg):.2f}"
                except ValueError:
                    pass
                    
            product.save(update_fields=['name', 'notes', 'accent_color', 'icon', 'unit_price', 'price_per_kg', 'pieces_per_kg', 'quantity_kg', 'updated_at'])
            messages.success(request, f'Product "{product.name}" updated successfully!')
        else:
            messages.error(request, 'Product name is required.')
        
    return redirect(next_url or 'sales:list')


@login_required
def delivery_create(request):
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response
    if request.method == 'POST':
        form = DeliveryForm(request.POST, user=request.user)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.created_by = request.user
            delivery.save()
            messages.success(request, f'Delivery for "{delivery.order.order_number}" created successfully!')

            if request.htmx:
                deliveries = Delivery.objects.select_related('order', 'created_by')

            return redirect('sales:list')
    else:
        form = DeliveryForm(user=request.user)

    if request.htmx:
        return render(request, 'sales_management/partials/delivery_form.html', {'form': form})

    return redirect('sales:list')


def customer_portal(request):
    guest_mode = not (request.user.is_authenticated and is_customer(request.user))
    customer = None
    if not guest_mode:
        customer = get_customer_profile(request.user)

    products = Product.objects.filter(is_active=True).select_related('species')
    orders = SalesOrder.objects.select_related('product').filter(customer=customer, status=SalesOrder.Status.PENDING) if customer else []
    deliveries = Delivery.objects.select_related('order').filter(order__customer=customer) if customer else []
    cart_orders_count = len(orders)

    context = {
        'products': products,
        'orders': orders,
        'deliveries': deliveries,
        'order_form': CustomerOrderForm() if not guest_mode else None,
        'location_form': CustomerLocationForm(instance=customer) if customer else None,
        'customer': customer,
        'active_page': 'market',
        'guest_mode': guest_mode,
        'cart_orders_count': cart_orders_count,
        'payment_settings': PaymentSetting.get_settings(),
    }
    return render(request, 'sales_management/customer_portal.html', context)


def customer_orders_page(request):
    customer, needs_login = _resolve_customer_profile(request)
    if needs_login or not customer:
        messages.error(request, 'Please log in to view your orders.')
        return redirect('customer_login')

    cart_orders_count = SalesOrder.objects.filter(customer=customer, status=SalesOrder.Status.PENDING).count()
    context = {
        'customer': customer,
        'products': Product.objects.filter(is_active=True).select_related('species'),
        'orders': SalesOrder.objects.select_related('product').filter(customer=customer).exclude(status=SalesOrder.Status.PENDING),
        'deliveries': Delivery.objects.select_related('order').filter(order__customer=customer),
        'order_form': CustomerOrderForm(),
        'location_form': CustomerLocationForm(instance=customer),
        'active_page': 'orders',
        'guest_mode': False,
        'cart_orders_count': cart_orders_count,
        'payment_settings': PaymentSetting.get_settings(),
    }
    return render(request, 'sales_management/customer_portal.html', context)





def customer_account_page(request):
    customer, needs_login = _resolve_customer_profile(request)
    if needs_login or not customer:
        messages.error(request, 'Please log in to access your account.')
        return redirect('customer_login')

    cart_orders_count = SalesOrder.objects.filter(customer=customer, status=SalesOrder.Status.PENDING).count()
    context = {
        'customer': customer,
        'products': Product.objects.filter(is_active=True).select_related('species'),
        'orders': SalesOrder.objects.select_related('product').filter(customer=customer),
        'deliveries': Delivery.objects.select_related('order').filter(order__customer=customer),
        'order_form': CustomerOrderForm(),
        'location_form': CustomerLocationForm(instance=customer),
        'active_page': 'account',
        'guest_mode': False,
        'cart_orders_count': cart_orders_count,
        'payment_settings': PaymentSetting.get_settings(),
    }
    return render(request, 'sales_management/customer_portal.html', context)


def customer_location_update(request):
    customer, needs_login = _resolve_customer_profile(request)
    if needs_login or not customer:
        from django.http import JsonResponse
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'address' in request.POST:
            return JsonResponse({'success': False, 'error': 'Please log in first.'})
        messages.error(request, 'Please log in first.')
        return redirect('customer_login')

    if request.method == 'POST':
        address = request.POST.get('address')
        if address:
            customer.address = address
            customer.save()
            # Also update pending cart orders delivery address
            from apps.sales.models import SalesOrder
            SalesOrder.objects.filter(customer=customer, status=SalesOrder.Status.PENDING).update(delivery_address=address)
        
        lat = request.POST.get('map_latitude')
        lng = request.POST.get('map_longitude')
        if lat and lng:
            customer.map_latitude = lat
            customer.map_longitude = lng
            customer.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'address' in request.POST:
            from django.http import JsonResponse
            return JsonResponse({'success': True})

        messages.success(request, 'Location updated successfully.')
    return redirect('sales:customer_account_page')


def customer_cart_page(request):
    customer, needs_login = _resolve_customer_profile(request)
    if needs_login or not customer:
        messages.error(request, 'Please log in to checkout.')
        return redirect('customer_login')

    orders = SalesOrder.objects.select_related('product').filter(customer=customer, status=SalesOrder.Status.PENDING)
    cart_orders_count = len(orders)
    context = {
        'customer': customer,
        'products': Product.objects.filter(is_active=True).select_related('species'),
        'orders': orders,
        'deliveries': Delivery.objects.select_related('order').filter(order__customer=customer),
        'order_form': CustomerOrderForm(),
        'location_form': CustomerLocationForm(instance=customer),
        'active_page': 'cart',
        'guest_mode': False,
        'cart_orders_count': cart_orders_count,
        'payment_settings': PaymentSetting.get_settings(),
    }
    return render(request, 'sales_management/customer_portal.html', context)


def customer_order_create(request):
    customer, needs_login = _resolve_customer_profile(request)
    if needs_login or not customer:
        messages.error(request, 'Please log in to place an order.')
        return redirect('customer_login')

    if request.method == 'POST':
        form = CustomerOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = customer
            order.order_number = generate_order_number()
            order.order_date = datetime.date.today()
            pricing_unit = request.POST.get('pricing_unit', 'pc')
            if order.product:
                if pricing_unit == 'kg' and order.product.price_per_kg and order.product.price_per_kg > 0:
                    order.price_per_kg = order.product.price_per_kg
                else:
                    order.price_per_kg = order.product.unit_price
            else:
                order.price_per_kg = 0

            order.discount = 0
            order.status = SalesOrder.Status.PENDING
            order.payment_status = SalesOrder.PaymentStatus.UNPAID
            order.order_type = (
                SalesOrder.OrderType.WHOLESALE
                if order.quantity_kg >= WHOLESALE_MIN_QTY_KG
                else SalesOrder.OrderType.RETAIL
            )
            if not order.delivery_address:
                order.delivery_address = customer.address
            order.created_by = request.user if request.user.is_authenticated else None
            
            unit_prefix = f"[{pricing_unit.upper()}]"
            if not order.notes or unit_prefix not in order.notes:
                order.notes = f"{unit_prefix} {order.notes or ''}".strip()
                
            order.total_amount = (order.quantity_kg * order.price_per_kg)
            order.save()

            if request.htmx:
                from django.http import HttpResponse
                response = HttpResponse()
                response['HX-Redirect'] = request.build_absolute_uri('/sales/market/cart/')
                return response

            return redirect('sales:customer_cart_page')
    else:
        form = CustomerOrderForm()

    if request.htmx:
        return render(request, 'sales_management/partials/customer_order_form.html', {'form': form})

    return redirect('sales:customer_portal')


def customer_order_update_quantity(request, order_id):
    if not request.user.is_authenticated:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=401)
    
    order = get_object_or_404(SalesOrder, id=order_id)
    customer = get_customer_profile(request.user)
    if not customer or order.customer != customer:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'error': 'Unauthorized'}, status=403)
        
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            qty = float(data.get('quantity', 1))
            if qty <= 0:
                from django.http import JsonResponse
                return JsonResponse({'success': False, 'error': 'Quantity must be positive'})
            
            order.quantity_kg = qty
            order.total_amount = qty * order.price_per_kg
            order.save()
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'total_amount': float(order.total_amount),
                'quantity_kg': float(order.quantity_kg)
            })
        except Exception as e:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': str(e)})
            
    from django.http import JsonResponse
    return JsonResponse({'success': False, 'error': 'POST request required'}, status=400)


def customer_order_delete(request, order_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in first.')
        return redirect('customer_login')
        
    customer = get_customer_profile(request.user)
    order = get_object_or_404(SalesOrder, id=order_id)
    if not customer or order.customer != customer:
        messages.error(request, 'Unauthorized action.')
        return redirect('sales:customer_orders_page')
        
    if order.status != SalesOrder.Status.PENDING:
        messages.error(request, 'Cannot remove a finalized order.')
        return redirect('sales:customer_orders_page')
        
    order.delete()
    messages.success(request, 'Item removed from your cart.')
    return redirect('sales:customer_orders_page')


def customer_checkout_submit(request):
    customer, needs_login = _resolve_customer_profile(request)
    if needs_login or not customer:
        from django.http import JsonResponse
        return JsonResponse({'success': False, 'error': 'Please log in first.'})

    if request.method == 'POST':
        import json
        import base64
        try:
            data = json.loads(request.body)
            order_ids = data.get('order_ids', [])
            payment_method = data.get('payment_method', 'cod')
            payment_reference = data.get('payment_reference', '').strip()
            receipt_base64 = data.get('receipt_image_base64')
        except Exception:
            order_ids = []
            payment_method = 'cod'
            payment_reference = ''
            receipt_base64 = None
            
        receipt_bytes = None
        if receipt_base64 and ',' in receipt_base64:
            try:
                header, encoded = receipt_base64.split(',', 1)
                receipt_bytes = base64.b64decode(encoded)
            except Exception:
                receipt_bytes = None
            
        from apps.sales.models import SalesOrder
        from django.urls import reverse
        if order_ids:
            orders_to_place = list(SalesOrder.objects.filter(customer=customer, id__in=order_ids, status=SalesOrder.Status.PENDING))
        else:
            orders_to_place = list(SalesOrder.objects.filter(customer=customer, status=SalesOrder.Status.PENDING))
            
        if not orders_to_place:
            from django.http import JsonResponse
            return JsonResponse({'success': False, 'error': 'No items found in cart.'})

        # Automated GCash Flow via PayMongo
        if payment_method == 'gcash':
            from apps.sales.paymongo_service import create_paymongo_checkout_session
            
            success_url = request.build_absolute_uri(reverse('sales:paymongo_success')) + f"?orders={','.join(str(o.id) for o in orders_to_place)}"
            cancel_url = request.build_absolute_uri(reverse('sales:customer_cart_page'))
            
            session_data = create_paymongo_checkout_session(orders_to_place, customer, success_url, cancel_url)
            
            # If live PayMongo checkout URL returned, redirect user straight to GCash OTP portal!
            if session_data.get('checkout_url'):
                for order in orders_to_place:
                    unit_info = "[KG] " if (order.notes and '[KG]' in order.notes) else ("[PC] " if (order.notes and '[PC]' in order.notes) else "")
                    order.notes = f"{unit_info}Payment: Automated GCash (Session #{session_data['id']})".strip()
                    order.save(update_fields=['notes'])
                from django.http import JsonResponse
                return JsonResponse({'success': True, 'redirect_url': session_data['checkout_url'], 'is_gateway': True})
            
            # Confirm GCash payment with verified reference
            ref_label = payment_reference if payment_reference else "Verified Online"
            for order in orders_to_place:
                order.status = SalesOrder.Status.CONFIRMED
                order.payment_status = SalesOrder.PaymentStatus.PAID
                unit_info = "[KG] " if (order.notes and '[KG]' in order.notes) else ("[PC] " if (order.notes and '[PC]' in order.notes) else "")
                order.notes = f"{unit_info}Payment: GCash ({ref_label})".strip()
                if receipt_bytes:
                    order.receipt_image = receipt_bytes
                order.save()
                if order.product and order.product.quantity_kg >= order.quantity_kg:
                    order.product.quantity_kg -= order.quantity_kg
                    order.product.save(update_fields=['quantity_kg'])
            from django.http import JsonResponse
            return JsonResponse({'success': True, 'redirect_url': reverse('sales:customer_orders_page'), 'is_gateway': False})

        # Cash / Cash on Delivery flow
        for order in orders_to_place:
            order.status = SalesOrder.Status.CONFIRMED
            order.payment_status = SalesOrder.PaymentStatus.UNPAID
            
            is_pickup = (order.delivery_address and order.delivery_address.upper() == 'PICKUP')
            method_label = "Cash" if is_pickup else "Cash on Delivery"
                
            unit_info = ""
            if order.notes and ('[KG]' in order.notes or '[PC]' in order.notes):
                unit_info = "[KG] " if '[KG]' in order.notes else "[PC] "
                
            order.notes = f"{unit_info}Payment: {method_label}".strip()
            order.save()
            
            if order.product and order.product.quantity_kg >= order.quantity_kg:
                order.product.quantity_kg -= order.quantity_kg
                order.product.save(update_fields=['quantity_kg'])
            
        from django.http import JsonResponse
        return JsonResponse({'success': True, 'redirect_url': reverse('sales:customer_orders_page'), 'is_gateway': False})

    from django.http import JsonResponse
    return JsonResponse({'success': False, 'error': 'POST required'})


def paymongo_payment_success(request):
    """Callback after successful automated GCash payment."""
    customer, needs_login = _resolve_customer_profile(request)
    order_ids_param = request.GET.get('orders', '')
    if order_ids_param:
        order_ids = [int(x) for x in order_ids_param.split(',') if x.isdigit()]
        from apps.sales.models import SalesOrder
        orders = SalesOrder.objects.filter(id__in=order_ids)
        for order in orders:
            order.status = SalesOrder.Status.CONFIRMED
            order.payment_status = SalesOrder.PaymentStatus.PAID
            unit_info = "[KG] " if (order.notes and '[KG]' in order.notes) else ("[PC] " if (order.notes and '[PC]' in order.notes) else "")
            order.notes = f"{unit_info}Payment: Automated GCash (Paid Online)".strip()
            order.save()
            if order.product and order.product.quantity_kg >= order.quantity_kg:
                order.product.quantity_kg -= order.quantity_kg
                order.product.save(update_fields=['quantity_kg'])
                
    messages.success(request, '🎉 Payment successful! Your order has been placed.')
    return redirect('sales:customer_orders_page')


@login_required
def delivery_list_page(request):
    """Delivery management module page."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    # Auto-sync delivery records for orders with delivery address
    all_orders = SalesOrder.objects.select_related('customer', 'product').all()
    missing_deliveries = all_orders.exclude(delivery_address__iexact='pickup').filter(deliveries__isnull=True)
    for ord_obj in missing_deliveries:
        if ord_obj.status in [SalesOrder.Status.DELIVERED, SalesOrder.Status.COMPLETED]:
            deliv_status = Delivery.Status.DELIVERED
            deliv_date = ord_obj.order_date
        elif ord_obj.status == SalesOrder.Status.CANCELLED:
            deliv_status = Delivery.Status.CANCELLED
            deliv_date = None
        elif ord_obj.status == SalesOrder.Status.SHIPPED:
            deliv_status = Delivery.Status.IN_TRANSIT
            deliv_date = None
        else:
            deliv_status = Delivery.Status.SCHEDULED
            deliv_date = None

        Delivery.objects.create(
            order=ord_obj,
            scheduled_date=ord_obj.order_date,
            delivered_date=deliv_date,
            delivery_location=ord_obj.delivery_address or "Standard Delivery",
            quantity_kg=ord_obj.quantity_kg,
            status=deliv_status,
            created_by=ord_obj.created_by
        )

    deliveries_qs = Delivery.objects.select_related('order', 'order__customer', 'order__product', 'rider', 'created_by').all()

    # Filter by status: Default to active deliveries only (scheduled + in transit)
    status_filter = request.GET.get('status', '').strip().lower()
    if status_filter == 'all':
        deliveries = deliveries_qs
    elif status_filter in [Delivery.Status.SCHEDULED, Delivery.Status.IN_TRANSIT, Delivery.Status.DELIVERED, Delivery.Status.CANCELLED]:
        deliveries = deliveries_qs.filter(status=status_filter)
    else:
        deliveries = deliveries_qs.filter(status__in=[Delivery.Status.SCHEDULED, Delivery.Status.IN_TRANSIT])

    # Search keyword
    query = request.GET.get('q', '').strip()
    if query:
        deliveries = deliveries.filter(
            Q(order__order_number__icontains=query) |
            Q(order__customer__name__icontains=query) |
            Q(order__customer__phone__icontains=query) |
            Q(delivery_location__icontains=query) |
            Q(rider__name__icontains=query) |
            Q(notes__icontains=query)
        )

    # Calculate statistics
    total_deliveries = deliveries_qs.count()
    scheduled_count = deliveries_qs.filter(status=Delivery.Status.SCHEDULED).count()
    in_transit_count = deliveries_qs.filter(status=Delivery.Status.IN_TRANSIT).count()
    delivered_count = deliveries_qs.filter(status=Delivery.Status.DELIVERED).count()
    cancelled_count = deliveries_qs.filter(status=Delivery.Status.CANCELLED).count()
    active_count = scheduled_count + in_transit_count
    total_kg = deliveries_qs.filter(status__in=[Delivery.Status.SCHEDULED, Delivery.Status.IN_TRANSIT]).aggregate(
        total=Sum('quantity_kg')
    )['total'] or Decimal('0')

    riders = Rider.objects.filter(is_active=True).order_by('name')
    form = DeliveryForm(user=request.user, initial={'scheduled_date': datetime.date.today()})

    context = {
        'deliveries': deliveries,
        'riders': riders,
        'form': form,
        'total_deliveries': total_deliveries,
        'active_count': active_count,
        'scheduled_count': scheduled_count,
        'in_transit_count': in_transit_count,
        'delivered_count': delivered_count,
        'cancelled_count': cancelled_count,
        'total_kg': total_kg,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'sales_management/delivery_list.html', context)


@login_required
def delivery_status_update(request, delivery_id):
    """Assign rider to delivery dispatch."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if request.method == 'POST':
        rider_id = request.POST.get('rider')
        if rider_id:
            try:
                assigned_rider = Rider.objects.get(id=rider_id)
                delivery.rider = assigned_rider
                delivery.save(update_fields=['rider'])
                messages.success(request, f'Rider "{assigned_rider.name}" assigned to order #{delivery.order.order_number}. The rider will accept and update transit in their Driver Portal.')
            except Rider.DoesNotExist:
                pass
        elif 'rider' in request.POST and not rider_id:
            delivery.rider = None
            delivery.save(update_fields=['rider'])
            messages.info(request, f'Rider unassigned from order #{delivery.order.order_number}.')

    next_url = request.POST.get('next') or request.GET.get('next') or 'sales:delivery_list'
    return redirect(next_url)


@login_required
def delivery_edit(request, delivery_id):
    """Edit delivery details."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if request.method == 'POST':
        form = DeliveryForm(request.POST, instance=delivery, user=request.user)
        if form.is_valid():
            deliv = form.save()
            if deliv.status == Delivery.Status.DELIVERED and not deliv.delivered_date:
                deliv.delivered_date = datetime.date.today()
                deliv.save(update_fields=['delivered_date'])
            messages.success(request, f'Delivery {deliv.order.order_number} updated successfully.')
            return redirect('sales:delivery_list')
    else:
        form = DeliveryForm(instance=delivery, user=request.user)

    return render(request, 'sales_management/partials/delivery_form.html', {'form': form, 'delivery': delivery})


@login_required
def delivery_delete(request, delivery_id):
    """Delete a delivery record."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    delivery = get_object_or_404(Delivery, pk=delivery_id)
    if request.method == 'POST':
        order_num = delivery.order.order_number
        delivery.delete()
        messages.success(request, f'Delivery for order {order_num} deleted.')
    return redirect('sales:delivery_list')


@login_required
def delivery_logs_page(request):
    """Delivery Audit and Logs page tracking approvals, receipts, proof of delivery, and completion dates."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    # Base queryset with relations
    logs_qs = Delivery.objects.select_related(
        'order', 'order__customer', 'order__product', 'order__created_by', 'rider', 'created_by'
    ).all()

    # Search query
    query = request.GET.get('q', '').strip()
    if query:
        logs_qs = logs_qs.filter(
            Q(order__order_number__icontains=query) |
            Q(order__customer__name__icontains=query) |
            Q(order__customer__phone__icontains=query) |
            Q(created_by__username__icontains=query) |
            Q(created_by__first_name__icontains=query) |
            Q(created_by__last_name__icontains=query) |
            Q(order__created_by__username__icontains=query) |
            Q(rider__name__icontains=query) |
            Q(delivery_location__icontains=query)
        )

    # Status filter
    status_filter = request.GET.get('status', 'all').strip().lower()
    if status_filter in [Delivery.Status.DELIVERED, Delivery.Status.IN_TRANSIT, Delivery.Status.SCHEDULED, Delivery.Status.CANCELLED]:
        filtered_logs = logs_qs.filter(status=status_filter)
    else:
        status_filter = 'all'
        filtered_logs = logs_qs

    # Ordering: Completed/Delivered orders first, then active/scheduled
    filtered_logs = filtered_logs.order_by(
        Case(
            When(status=Delivery.Status.DELIVERED, then=Value(0)),
            When(status=Delivery.Status.IN_TRANSIT, then=Value(1)),
            When(status=Delivery.Status.SCHEDULED, then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        ),
        F('delivered_date').desc(nulls_last=True),
        '-created_at'
    )

    # Aggregates / Stats
    total_logs = Delivery.objects.count()
    delivered_count = Delivery.objects.filter(status=Delivery.Status.DELIVERED).count()
    in_transit_count = Delivery.objects.filter(status=Delivery.Status.IN_TRANSIT).count()
    scheduled_count = Delivery.objects.filter(status=Delivery.Status.SCHEDULED).count()

    delivered_qs = Delivery.objects.filter(status=Delivery.Status.DELIVERED)
    total_delivered_kg = delivered_qs.aggregate(total=Sum('quantity_kg'))['total'] or Decimal('0')
    total_delivered_revenue = delivered_qs.aggregate(total=Sum('order__total_amount'))['total'] or Decimal('0')

    # Pagination: 15 per page
    paginator = Paginator(filtered_logs, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'deliveries': page_obj,
        'page_obj': page_obj,
        'total_logs': total_logs,
        'delivered_count': delivered_count,
        'in_transit_count': in_transit_count,
        'scheduled_count': scheduled_count,
        'total_delivered_kg': total_delivered_kg,
        'total_delivered_revenue': total_delivered_revenue,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'sales_management/delivery_logs.html', context)


@login_required
def delivery_track_page(request):
    """Live GPS Delivery Tracking page for staff and owners."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    all_deliveries_qs = Delivery.objects.select_related(
        'order', 'order__customer', 'order__product', 'order__created_by', 'rider', 'created_by'
    ).all()

    active_deliveries = all_deliveries_qs.filter(
        status__in=[Delivery.Status.IN_TRANSIT, Delivery.Status.SCHEDULED]
    ).order_by(
        Case(
            When(status=Delivery.Status.IN_TRANSIT, then=Value(0)),
            When(status=Delivery.Status.SCHEDULED, then=Value(1)),
            default=Value(2),
            output_field=IntegerField(),
        ),
        '-scheduled_date', '-created_at'
    )

    recent_completed = all_deliveries_qs.filter(
        status=Delivery.Status.DELIVERED
    ).order_by('-delivered_date', '-created_at')[:10]

    selected_delivery = None
    query = request.GET.get('q', '').strip()
    delivery_id = request.GET.get('id', '').strip()

    if delivery_id and delivery_id.isdigit():
        selected_delivery = all_deliveries_qs.filter(id=int(delivery_id)).first()
    elif query:
        selected_delivery = all_deliveries_qs.filter(
            Q(order__order_number__iexact=query) |
            Q(order__order_number__icontains=query) |
            Q(order__customer__name__icontains=query) |
            Q(order__customer__phone__icontains=query)
        ).first()

    if not selected_delivery:
        selected_delivery = active_deliveries.first() or recent_completed.first() or all_deliveries_qs.first()

    context = {
        'selected_delivery': selected_delivery,
        'active_deliveries': active_deliveries,
        'recent_completed': recent_completed,
        'query': query,
    }
    return render(request, 'sales_management/track_order.html', context)


# ============================================================
# RIDERS MANAGEMENT VIEWS
# ============================================================

@login_required
def rider_list_page(request):
    """Riders management sub-page."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    riders_qs = Rider.objects.filter(is_active=True).prefetch_related('deliveries')

    status_filter = request.GET.get('status', '').strip().lower()
    if status_filter and status_filter in [Rider.Status.AVAILABLE, Rider.Status.ON_DELIVERY, Rider.Status.OFF_DUTY]:
        riders = riders_qs.filter(status=status_filter)
    else:
        riders = riders_qs

    query = request.GET.get('q', '').strip()
    if query:
        riders = riders.filter(
            Q(name__icontains=query) |
            Q(phone__icontains=query) |
            Q(vehicle_type__icontains=query) |
            Q(plate_number__icontains=query) |
            Q(notes__icontains=query)
        )

    total_riders = riders_qs.count()
    available_count = riders_qs.filter(status=Rider.Status.AVAILABLE).count()
    on_delivery_count = riders_qs.filter(status=Rider.Status.ON_DELIVERY).count()
    off_duty_count = riders_qs.filter(status=Rider.Status.OFF_DUTY).count()

    form = RiderForm()

    context = {
        'riders': riders,
        'form': form,
        'total_riders': total_riders,
        'available_count': available_count,
        'on_delivery_count': on_delivery_count,
        'off_duty_count': off_duty_count,
        'status_filter': status_filter,
        'query': query,
    }
    return render(request, 'sales_management/rider_list.html', context)


@login_required
def rider_create(request):
    """Create a new rider and linked user account."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    if request.method == 'POST':
        form = RiderForm(request.POST)
        password = request.POST.get('password', '').strip()

        if not password:
            messages.error(request, 'Password is required to create a rider login account.')
            return redirect('sales:rider_list')

        if form.is_valid():
            rider = form.save(commit=False)
            phone = rider.phone.strip()
            name = rider.name.strip()

            # Create or link User account using phone as username
            user = User.objects.filter(username__iexact=phone).first()
            if not user:
                user = User(
                    username=phone,
                    first_name=name,
                    phone=phone,
                    role=User.Role.RIDER,
                    is_active=True,
                )
                user.set_password(password)
                user.save()
            else:
                user.role = User.Role.RIDER
                user.set_password(password)
                user.save()

            rider.user = user
            rider.save()
            messages.success(request, f'Rider "{rider.name}" and account ({phone}) created successfully!')
        else:
            messages.error(request, 'Failed to add rider. Please check the inputs.')
    return redirect('sales:rider_list')


@login_required
def rider_edit(request, rider_id):
    """Edit rider information."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    rider = get_object_or_404(Rider, pk=rider_id)
    if request.method == 'POST':
        form = RiderForm(request.POST, instance=rider)
        if form.is_valid():
            form.save()
            messages.success(request, f'Rider "{rider.name}" updated successfully.')
        else:
            messages.error(request, 'Failed to update rider.')
    return redirect('sales:rider_list')


@login_required
def rider_status_update(request, rider_id):
    """Quick update rider status."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    rider = get_object_or_404(Rider, pk=rider_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in [s.value for s in Rider.Status]:
            rider.status = new_status
            rider.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Rider "{rider.name}" is now {rider.get_status_display()}.')
        else:
            messages.error(request, 'Invalid rider status.')
    return redirect('sales:rider_list')


@login_required
def rider_delete(request, rider_id):
    """Delete a rider and clean up linked user."""
    access_response = _ensure_sales_owner(request)
    if access_response:
        return access_response

    rider = get_object_or_404(Rider, pk=rider_id)
    if request.method == 'POST':
        name = rider.name
        user = rider.user
        # Unlink any deliveries assigned to this rider first
        rider.deliveries.update(rider=None)
        rider.delete()
        if user and user.role == User.Role.RIDER:
            user.delete()
        messages.success(request, f'Rider "{name}" removed from registry.')
    return redirect('sales:rider_list')


# ============================================================
# RIDER DRIVER APP / PORTAL VIEWS (Grab-inspired Experience)
# ============================================================

@login_required
def rider_portal(request):
    """
    Grab-inspired Driver App for Couriers:
    Shows assigned dispatches, pickup/dropoff routing, customer contact,
    interactive location pin map, and one-tap status updates.
    """
    if is_customer(request.user):
        return redirect('sales:customer_portal')

    rider = get_rider_profile(request.user)
    if not rider:
        if is_rider(request.user):
            rider = Rider.objects.create(
                user=request.user,
                name=request.user.get_full_name() or request.user.username,
                phone=request.user.phone or request.user.username,
                vehicle_type="Motorcycle",
                status=Rider.Status.AVAILABLE,
            )
        else:
            messages.error(request, 'You do not have rider driver permissions.')
            return redirect('dashboard')

    deliveries_qs = Delivery.objects.filter(rider=rider).select_related('order', 'order__customer', 'order__product').order_by('-scheduled_date', '-id')

    active_deliveries = deliveries_qs.filter(status__in=[Delivery.Status.SCHEDULED, Delivery.Status.IN_TRANSIT])
    completed_deliveries = deliveries_qs.filter(status=Delivery.Status.DELIVERED)

    # Available / Unassigned delivery dispatches that riders can claim
    available_deliveries = Delivery.objects.filter(
        rider__isnull=True,
        status=Delivery.Status.SCHEDULED
    ).exclude(
        delivery_location__iexact='pickup'
    ).select_related('order', 'order__customer', 'order__product').order_by('-scheduled_date', '-id')

    active_count = active_deliveries.count()
    available_count = available_deliveries.count()
    in_transit_count = active_deliveries.filter(status=Delivery.Status.IN_TRANSIT).count()
    completed_count = completed_deliveries.count()
    total_volume_today = deliveries_qs.filter(delivered_date=datetime.date.today()).aggregate(total=Sum('quantity_kg'))['total'] or 0

    context = {
        'rider': rider,
        'available_deliveries': available_deliveries,
        'available_count': available_count,
        'active_deliveries': active_deliveries,
        'completed_deliveries': completed_deliveries,
        'active_count': active_count,
        'in_transit_count': in_transit_count,
        'completed_count': completed_count,
        'total_volume_today': total_volume_today,
    }
    return render(request, 'sales_management/rider_portal.html', context)


@login_required
def rider_delivery_action(request, delivery_id):
    """Update delivery progress by rider (Claim / Start transit / Mark delivered)."""
    rider = get_rider_profile(request.user)
    if not rider:
        messages.error(request, 'Rider access required.')
        return redirect('sales:rider_portal')

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'claim_order':
            delivery = get_object_or_404(Delivery, pk=delivery_id, rider__isnull=True)
            delivery.rider = rider
            delivery.save(update_fields=['rider'])
            messages.success(request, f'Order #{delivery.order.order_number} accepted! It is now in your active deliveries.')
            return redirect('sales:rider_portal')

        delivery = get_object_or_404(Delivery, pk=delivery_id, rider=rider)
        if action == 'start_transit':
            delivery.status = Delivery.Status.IN_TRANSIT
            delivery.save(update_fields=['status'])
            rider.status = Rider.Status.ON_DELIVERY
            rider.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Delivery #{delivery.order.order_number} is now IN TRANSIT! Drive safely.')
        elif action == 'mark_delivered':
            delivery.status = Delivery.Status.DELIVERED
            delivery.delivered_date = datetime.date.today()
            delivery.save(update_fields=['status', 'delivered_date'])
            if not rider.deliveries.filter(status=Delivery.Status.IN_TRANSIT).exists():
                rider.status = Rider.Status.AVAILABLE
                rider.save(update_fields=['status', 'updated_at'])
            messages.success(request, f'Order #{delivery.order.order_number} marked as DELIVERED!')
    return redirect('sales:rider_portal')


@login_required
def rider_portal_duty_toggle(request):
    """Toggle online / offline duty status by rider."""
    rider = get_rider_profile(request.user)
    if not rider:
        return redirect('sales:rider_portal')

    if request.method == 'POST':
        if rider.status == Rider.Status.OFF_DUTY:
            rider.status = Rider.Status.AVAILABLE
            messages.success(request, 'You are now ONLINE and available for delivery dispatches!')
        else:
            rider.status = Rider.Status.OFF_DUTY
            messages.info(request, 'You are now OFF DUTY.')
        rider.save(update_fields=['status', 'updated_at'])
    return redirect('sales:rider_portal')


