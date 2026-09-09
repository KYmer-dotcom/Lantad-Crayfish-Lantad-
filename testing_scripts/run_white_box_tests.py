"""
White-Box Test Suite Runner for Lantad Superworm & Crayfish Farm Management System
Executes the 16 White-Box structural unit test cases (Security, Production, Sales/Billing)
and outputs structured terminal verification evidence.
"""
import os
import sys
import unittest
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_DIR = os.path.join(BASE_DIR, "System")
if SYSTEM_DIR not in sys.path:
    sys.path.insert(0, SYSTEM_DIR)
os.chdir(SYSTEM_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.test.runner import DiscoverRunner

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def run_white_box_tests():
    print("=" * 80)
    print(" AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM - WHITE-BOX TEST RUNNER")
    print("=" * 80)
    print("Testing internal code logic, algorithms, RBAC guards, and database transactions.\n")
    
    runner = DiscoverRunner(verbosity=2, interactive=False)
    
    suites = [
        ('Pillar 1: Security & RBAC Guards', 'apps.accounts.tests'),
        ('Pillar 2: Production Lifecycle & Inventory Logic', 'apps.stock.tests'),
        ('Pillar 3: Sales, PayMongo & Billing Transactions', 'apps.sales.tests')
    ]
    
    total_failures = 0
    start_total = time.time()
    
    for title, module_path in suites:
        print(f"\n--- [RUNNING] {title} ({module_path}) ---")
        failures = runner.run_tests([module_path])
        total_failures += failures
        if failures == 0:
            print(f"[PASS] {title}: PASSED")
        else:
            print(f"[FAIL] {title}: {failures} FAILURES")
            
    total_elapsed = time.time() - start_total
    
    print("\n" + "=" * 80)
    print(" WHITE-BOX TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"Total Test Duration : {total_elapsed:.2f} seconds")
    print(f"Total Test Suites   : {len(suites)}")
    if total_failures == 0:
        print("Final Test Status   : [PASS] 100% VERIFIED PASS (0 Errors, 0 Failures)")
        print("=" * 80)
        sys.exit(0)
    else:
        print(f"Final Test Status   : [FAIL] {total_failures} TESTS FAILED")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    run_white_box_tests()
