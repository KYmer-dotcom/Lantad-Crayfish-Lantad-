# Aquaculture Value Chain Management System - Python Testing Scripts

This directory contains automated testing scripts for executing unit tests, white-box structural suites, and black-box endpoint validations for the Aquaculture Value Chain Management System with Predictive Analytics.

## Available Scripts

### 1. `run_all_tests.py`
Executes all Django test suites across the 7 core apps (`accounts`, `analytics`, `feed`, `harvest`, `operations`, `sales`, `stock`).
```bash
py -3 testing_scripts/run_all_tests.py
```

### 2. `run_white_box_tests.py`
Runs the 16 White-Box structural unit tests (RBAC Security, Production Lifecycle & Dual-Pricing, and Sales & PayMongo Billing).
```bash
py -3 testing_scripts/run_white_box_tests.py
```

### 3. `verify_system_endpoints.py`
Performs automated HTTP route verification for login, registration, public storefront, shopping cart, and authenticated redirect guards.
```bash
py -3 testing_scripts/verify_system_endpoints.py
```
