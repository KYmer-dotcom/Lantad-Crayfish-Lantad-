"""
Template views for Sales module
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django import forms
from decimal import Decimal
import datetime
from .models import Customer, SalesOrder


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
        fields = ['customer', 'order_date', 'quantity_kg', 'price_per_kg', 'discount', 'status', 'payment_status', 'delivery_address', 'notes']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'id': 'order_customer'
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


def generate_order_number():
    """Generate unique order number"""
    today = datetime.date.today()
    prefix = f"SO-{today.strftime('%Y%m%d')}"
    count = SalesOrder.objects.filter(order_number__startswith=prefix).count() + 1
    return f"{prefix}-{count:04d}"


@login_required
def sales_list(request):
    """List all customers and sales orders with summary stats"""
    customers = Customer.objects.filter(is_active=True).annotate(
        total_purchases_amount=Sum('orders__total_amount', filter=Q(orders__status='completed'))
    )
    orders = SalesOrder.objects.select_related('customer').all()
    
    # Summary stats
    total_customers = customers.count()
    total_revenue = orders.filter(status='completed').aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    pending_orders = orders.filter(status='pending').count()
    
    context = {
        'customers': customers,
        'orders': orders,
        'customer_form': CustomerForm(),
        'order_form': SalesOrderForm(initial={'order_date': datetime.date.today(), 'discount': 0}),
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
    }
    return render(request, 'sales/list.html', context)


@login_required
def customer_create(request):
    """Create a new customer"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            messages.success(request, f'Customer "{customer.name}" created successfully!')
            
            if request.htmx:
                customers = Customer.objects.filter(is_active=True).annotate(
                    total_purchases_amount=Sum('orders__total_amount', filter=Q(orders__status='completed'))
                )
                return render(request, 'sales/partials/customers_table.html', {'customers': customers})
            
            return redirect('sales:list')
    else:
        form = CustomerForm()
    
    if request.htmx:
        return render(request, 'sales/partials/customer_form.html', {'form': form})
    
    return redirect('sales:list')


@login_required
def order_create(request):
    """Create a new sales order"""
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_number = generate_order_number()
            order.total_amount = (order.quantity_kg * order.price_per_kg) - order.discount
            order.created_by = request.user
            order.save()
            messages.success(request, f'Order "{order.order_number}" created successfully!')
            
            if request.htmx:
                orders = SalesOrder.objects.select_related('customer').all()
                return render(request, 'sales/partials/orders_table.html', {'orders': orders})
            
            return redirect('sales:list')
    else:
        form = SalesOrderForm()
    
    if request.htmx:
        return render(request, 'sales/partials/order_form.html', {'form': form})
    
    return redirect('sales:list')
