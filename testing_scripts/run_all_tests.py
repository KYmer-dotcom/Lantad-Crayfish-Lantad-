"""
Automated Test Suite Runner for Lantad Superworm & Crayfish Farm Management System
Runs all Django unit test suites across all registered applications.
"""
import os
import sys
import time

# Add System directory to sys.path and chdir
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_DIR = os.path.join(BASE_DIR, "System")
if SYSTEM_DIR not in sys.path:
    sys.path.insert(0, SYSTEM_DIR)
os.chdir(SYSTEM_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.test.utils import get_runner
from django.conf import settings

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def run_suite():
    print("=" * 75)
    print(" AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM - TEST RUNNER")
    print("=" * 75)
    print("Executing all application unit test suites...")
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    
    test_labels = [
        'apps.accounts',
        'apps.analytics',
        'apps.feed',
        'apps.harvest',
        'apps.operations',
        'apps.sales',
        'apps.stock'
    ]
    
    start_time = time.time()
    failures = test_runner.run_tests(test_labels)
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 75)
    print(f"TEST EXECUTION SUMMARY: Completed in {elapsed:.2f}s")
    if failures:
        print(f"[FAIL] STATUS: FAILED ({failures} test failures detected)")
        sys.exit(1)
    else:
        print("[SUCCESS] STATUS: ALL TESTS PASSED SUCCESSFULLY (100% Pass Rate)")
        sys.exit(0)

if __name__ == "__main__":
    run_suite()
