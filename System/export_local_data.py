import os
import sys
import json
import django
from io import StringIO
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local_dump.json')
print(f"Exporting local database to {output_path} with UTF-8 encoding...")

buffer = StringIO()
call_command(
    'dumpdata',
    '--natural-foreign',
    '--natural-primary',
    '-e', 'contenttypes',
    '-e', 'auth.Permission',
    '--indent', '2',
    stdout=buffer
)

data = json.loads(buffer.getvalue())

# Sanitize any test secret keys so GitHub push protection doesn't flag them
for item in data:
    if item.get('model') == 'sales.paymentsetting':
        fields = item.get('fields', {})
        if 'paymongo_secret_key' in fields and fields['paymongo_secret_key'].startswith('sk_test_'):
            fields['paymongo_secret_key'] = 'sk_test_placeholder_key_for_demo'

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Export and sanitize completed successfully!")
