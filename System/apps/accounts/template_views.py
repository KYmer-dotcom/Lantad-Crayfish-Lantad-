"""
Template views for Accounts module
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied

from .models import User
from apps.sales.models import Customer
from .access import is_owner


@login_required
def user_list(request):
    if not is_owner(request.user):
        raise PermissionDenied("Only owners can manage accounts.")
    users = User.objects.filter(role=User.Role.OWNER).order_by('-date_joined')
    customers = Customer.objects.filter(is_active=True).order_by('name')
    context = {
        'users': users,
        'customers': customers,
    }
    return render(request, 'accounts/list.html', context)


@login_required
def customer_remove(request, customer_id):
    if not is_owner(request.user):
        raise PermissionDenied("Only owners can manage accounts.")

    customer = get_object_or_404(Customer, pk=customer_id)
    linked_user = customer.user
    customer_name = customer.name
    customer.delete()
    if linked_user:
        linked_user.delete()
    messages.success(request, f'Customer "{customer_name}" removed successfully.')
    return redirect('accounts:list')
