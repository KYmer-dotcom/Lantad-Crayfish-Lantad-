from django.db import models
from django.conf import settings
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        """Bulk soft-delete matching rows."""
        update_kwargs = {
            'is_deleted': True,
            'deleted_at': timezone.now(),
        }
        if hasattr(self.model, 'is_active'):
            update_kwargs['is_active'] = False
        return self.update(**update_kwargs)

    def hard_delete(self):
        """Permanent removal from database."""
        return super().delete()

    def restore(self):
        """Bulk restore matching soft-deleted rows."""
        update_kwargs = {
            'is_deleted': False,
            'deleted_at': None,
            'deleted_by': None,
        }
        if hasattr(self.model, 'is_active'):
            update_kwargs['is_active'] = True
        return self.update(**update_kwargs)

    def alive(self):
        """Only non-deleted rows."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Only archived / soft-deleted rows."""
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.alive_only:
            return qs.filter(is_deleted=False)
        return qs


class SoftDeleteModel(models.Model):
    """
    Abstract base model providing soft delete and data archiving functionality.
    Maintains is_deleted, deleted_at, and deleted_by.
    Automatically keeps is_active in sync if present on child model.
    """
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True
        base_manager_name = 'all_objects'
        default_manager_name = 'objects'

    def soft_delete(self, user=None):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        if user is not None and getattr(user, 'is_authenticated', False):
            self.deleted_by = user
        if hasattr(self, 'is_active'):
            self.is_active = False
        self.save()

    def delete(self, using=None, keep_parents=False, user=None):
        """Default delete performs a soft delete instead of hard delete."""
        self.soft_delete(user=user)

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        if hasattr(self, 'is_active'):
            self.is_active = True
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """Permanently delete row from database."""
        return super().delete(using=using, keep_parents=keep_parents)
