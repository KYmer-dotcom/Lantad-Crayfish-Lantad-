from django.db import migrations


def reassign_customer_deliveries_to_owner(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    Delivery = apps.get_model('sales', 'Delivery')
    
    owner = User.objects.filter(role='owner').order_by('id').first()
    if owner:
        # Reassign any delivery records created by customers or null to the owner
        Delivery.objects.filter(created_by__role='customer').update(created_by=owner)
        Delivery.objects.filter(created_by__isnull=True).update(created_by=owner)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0013_alter_product_managers_alter_salesorder_managers_and_more'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(reassign_customer_deliveries_to_owner, noop_reverse),
    ]
