from django.core.exceptions import PermissionDenied

from apps.operations.models import Pond, Farm
from apps.sales.models import Customer


def is_owner(user):
    return user.is_authenticated and (user.is_superuser or getattr(user, 'is_owner', False) or getattr(user, 'role', '') == 'owner')


def is_customer(user):
    if not user.is_authenticated or user.is_superuser or getattr(user, 'role', '') == 'owner':
        return False
    return getattr(user, 'is_customer', False) or getattr(user, 'role', '') == 'customer'


def is_rider(user):
    if not user.is_authenticated or user.is_superuser or getattr(user, 'role', '') == 'owner':
        return False
    return getattr(user, 'is_rider', False) or getattr(user, 'role', '') == 'rider'


def get_accessible_ponds(user):
    return Pond.objects.all()


def get_accessible_farms(user):
    return Farm.objects.all()


def filter_by_pond(user, queryset, pond_lookup="pond"):
    return queryset


def get_customer_profile(user):
    if not user or not user.is_authenticated:
        return None
    from apps.sales.models import Customer
    cust = Customer.objects.filter(user=user).first()
    if cust:
        return cust
    return Customer.objects.filter(phone=user.username).first()


def get_rider_profile(user):
    if not user or not user.is_authenticated:
        return None
    from apps.sales.models import Rider
    rider = Rider.objects.filter(user=user).first()
    if rider:
        return rider
    user_phone = getattr(user, 'phone', None)
    if user_phone:
        rider = Rider.objects.filter(phone=user_phone).first()
        if rider:
            return rider
    return Rider.objects.filter(phone=user.username).first()


def ensure_not_customer(user):
    if is_customer(user):
        raise PermissionDenied("Customers cannot access this section.")
    if is_rider(user):
        raise PermissionDenied("Riders only have access to the Driver Portal.")
