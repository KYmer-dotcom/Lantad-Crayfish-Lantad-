"""
Automated Endpoint & Black-Box Route Verification Script
Validates system URL routing, HTTP status codes, redirection guards, and public storefront endpoints.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_DIR = os.path.join(BASE_DIR, "System")
if SYSTEM_DIR not in sys.path:
    sys.path.insert(0, SYSTEM_DIR)
os.chdir(SYSTEM_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from django.test import Client
from django.urls import reverse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def verify_endpoints():
    print("=" * 80)
    print(" AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM - AUTOMATED ENDPOINT VERIFICATION")
    print("=" * 80)
    
    client = Client()
    
    endpoints = [
        ("Login Page", reverse("login"), [200]),
        ("Customer Login Page", reverse("customer_login"), [200]),
        ("Customer Register Page", reverse("customer_register"), [200]),
        ("Customer Storefront / Market", reverse("sales:customer_portal"), [200]),
        ("Customer Cart Page (Unauthenticated)", reverse("sales:customer_cart_page"), [200, 302]),
        ("Dashboard (Unauthenticated Redirect)", reverse("dashboard"), [302]),
        ("Inventory Overview (Unauthenticated Redirect)", reverse("inventory"), [302]),
        ("Delivery Driver Portal (Unauthenticated Redirect)", reverse("sales:rider_portal"), [302]),
        ("API Accounts Root", "/api/accounts/users/", [200, 401, 403]),
        ("API Operations Ponds Root", "/api/operations/ponds/", [200, 401, 403]),
    ]
    
    passed = 0
    failed = 0
    
    for name, url, expected_statuses in endpoints:
        response = client.get(url)
        status = response.status_code
        if status in expected_statuses:
            print(f"[PASS] {name:<42} | URL: {url:<25} | Status: {status}")
            passed += 1
        else:
            print(f"[FAIL] {name:<42} | URL: {url:<25} | Got {status}, expected {expected_statuses}")
            failed += 1
            
    print("-" * 80)
    print(f"Total Routes Checked: {len(endpoints)} | Passed: {passed} | Failed: {failed}")
    print("=" * 80)

if __name__ == "__main__":
    verify_endpoints()
