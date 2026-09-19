"""
Automated Test Suite Runner for Stock & Species Management App
Tests species lifecycle defaults, string representations, stock aggregation, batch growth, and survival rate computations.
"""
import os
import sys
import time

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
    print(" [CORE APP 7/7] STOCK & SPECIES MANAGEMENT TEST SUITE")
    print("=" * 75)
    print("Executing tests for 'apps.stock'...\n")
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=False)
    
    start_time = time.time()
    failures = test_runner.run_tests(['apps.stock'])
    elapsed = time.time() - start_time
    
    print("\n" + "=" * 75)
    print(f"STOCK TEST SUMMARY: Completed in {elapsed:.2f}s")
    if failures:
        print(f"[FAIL] STATUS: FAILED ({failures} test failures detected)")
        sys.exit(1)
    else:
        print("[SUCCESS] STATUS: ALL STOCK TESTS PASSED (100% Pass Rate)")
        sys.exit(0)

if __name__ == "__main__":
    run_suite()
