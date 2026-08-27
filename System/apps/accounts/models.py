"""
=============================================================================
ACCOUNTS MODULE - User Authentication & Role Management
=============================================================================
Handles user authentication, registration, and role-based access control.
Roles: OWNER (full access) | MANAGER (operational access)
=============================================================================
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with role-based access control."""
    
    class Role(models.TextChoices):
        OWNER = 'owner', 'Owner'
        CUSTOMER = 'customer', 'Customer'
        RIDER = 'rider', 'Rider'
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CUSTOMER
    )
    phone = models.CharField(max_length=20, blank=True)

    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_owner(self):
        return self.role == self.Role.OWNER
    
    @property
    def is_customer(self):
        return self.role == self.Role.CUSTOMER

    @property
    def is_rider(self):
        return self.role == self.Role.RIDER

    def save(self, *args, **kwargs):
        if self.role == self.Role.OWNER:
            self.is_staff = True
        elif not self.is_superuser:
            self.is_staff = False
        super().save(*args, **kwargs)
