#!/usr/bin/env python
"""Root proxy manage.py to run commands without cd into System."""
import os
import sys

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    system_dir = os.path.join(root_dir, 'System')
    
    sys.path.insert(0, system_dir)
    os.chdir(system_dir)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
