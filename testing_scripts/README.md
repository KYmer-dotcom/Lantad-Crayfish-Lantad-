# Aquaculture Value Chain Management System - Python Testing Scripts

This directory contains automated testing scripts for executing unit tests, white-box structural suites, black-box endpoint validations, and modular app-specific test runners.

## Available Scripts

### Master Test Runners
1. **`run_all_tests.py`**
   - Runs all 29 Django unit tests across all 7 core apps simultaneously.
   - Command: `py -3 testing_scripts/run_all_tests.py`

2. **`run_white_box_tests.py`**
   - Runs the 16 White-Box structural unit tests (RBAC Security, Production Lifecycle & Dual-Pricing, Sales & PayMongo Billing).
   - Command: `py -3 testing_scripts/run_white_box_tests.py`

3. **`verify_system_endpoints.py`**
   - Performs automated HTTP route verification for login, registration, public storefront, shopping cart, and RBAC redirect guards.
   - Command: `py -3 testing_scripts/verify_system_endpoints.py`

---

### Individual Core App Test Runners (7 Apps)
1. **`run_accounts_tests.py`**
   - Tests `apps.accounts` (RBAC permissions, role predicates, PayMongo auth headers, singleton settings).
   - Command: `py -3 testing_scripts/run_accounts_tests.py`

2. **`run_analytics_tests.py`**
   - Tests `apps.analytics` (Linear regression trends, rolling moving average forecasts, recommendation engine, dual pricing).
   - Command: `py -3 testing_scripts/run_analytics_tests.py`

3. **`run_feed_tests.py`**
   - Tests `apps.feed` (Feed inventory, movement tracking ledger, feed types).
   - Command: `py -3 testing_scripts/run_feed_tests.py`

4. **`run_harvest_tests.py`**
   - Tests `apps.harvest` (Harvest records, yield computations, forecasting schedules).
   - Command: `py -3 testing_scripts/run_harvest_tests.py`

5. **`run_operations_tests.py`**
   - Tests `apps.operations` (Farms, pond capacities, operational lifecycle state transitions).
   - Command: `py -3 testing_scripts/run_operations_tests.py`

6. **`run_sales_tests.py`**
   - Tests `apps.sales` (Inventory deduction atomicity, delivery state machine, rider load, PayMongo sessions, InputLog audit trails).
   - Command: `py -3 testing_scripts/run_sales_tests.py`

7. **`run_stock_tests.py`**
   - Tests `apps.stock` (Species models, stock tracking aggregations, batch survival rate computations).
   - Command: `py -3 testing_scripts/run_stock_tests.py`
