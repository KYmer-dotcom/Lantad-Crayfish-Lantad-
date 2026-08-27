import os
from django.core.management.base import BaseCommand
from apps.accounts.models import User


class Command(BaseCommand):
    help = 'Automatically create default admin/owner superuser if none exists.'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@lantad.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                role=User.Role.OWNER,
            )
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully with role OWNER.'))
        else:
            user = User.objects.get(username=username)
            if not user.is_superuser or user.role != User.Role.OWNER:
                user.is_superuser = True
                user.is_staff = True
                user.role = User.Role.OWNER
                user.save()
                self.stdout.write(self.style.SUCCESS(f'User "{username}" updated to superuser/owner.'))
            else:
                self.stdout.write(f'Superuser "{username}" already exists.')
