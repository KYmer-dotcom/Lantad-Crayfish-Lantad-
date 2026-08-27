from django.core.exceptions import PermissionDenied

from apps.operations.models import Pond, Farm
from apps.sales.models import Customer


def is_owner(user):
    return user.is_authenticated and (getattr(user, 'is_owner', False) or user.is_superuser or user.role == 'owner')


def is_customer(user):
    return user.is_authenticated and (getattr(user, 'is_customer', False) or user.role == 'customer')


def is_rider(user):
    return user.is_authenticated and (getattr(user, 'is_rider', False) or user.role == 'rider')


def get_accessible_ponds(user):
    return Pond.objects.all()


def get_accessible_farms(user):
    return Farm.objects.all()


def filter_by_pond(user, queryset, pond_lookup="pond"):
    return queryset


def get_customer_profile(user):
    if not is_customer(user):
        return None
    return Customer.objects.filter(user=user).first()


def get_rider_profile(user):
    if not is_rider(user):
        return None
    from apps.sales.models import Rider
    return Rider.objects.filter(user=user).first() or Rider.objects.filter(phone=user.username).first()


def ensure_not_customer(user):
    if is_customer(user):
        raise PermissionDenied("Customers cannot access this section.")
    if is_rider(user):
        raise PermissionDenied("Riders only have access to the Driver Portal.")
