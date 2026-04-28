
# AquaFarm - Value Chain Management System

A full-featured aquaculture management system built entirely with Django.

## 📁 Project Structure

```
MCC PUNONG/
└── backend/                 # Django Project
    ├── accounts/           # 👤 User Authentication & Roles
    ├── ponds/              # 🏞️ Pond and Farm Management
    ├── fish/               # 🐟 Fish Stocking & Classification
    ├── feed/               # 🌾 Feed Consumption Tracking
    ├── growth/             # 📈 Growth & Mortality Monitoring
    ├── harvest/            # 🎣 Harvest Management
    ├── sales/              # 💰 Sales & Distribution
    ├── analytics/          # 📊 Data Analytics & Forecasting
    └── core/               # ⚙️ Project Settings
```


## 🚀 Quick Start

### 1. Start the Server
```bash
cd backend
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
Server runs at: http://localhost:8000

## 🔐 Login Credentials
- **Username:** admin
- **Password:** admin123
- **Role:** Owner (Full Access)

## 📦 Modules

| Module | Description |
|--------|-------------|
| **Farms & Ponds** | Manage farms, ponds, water quality |
| **Fish Stocking** | Species, batches, stocking records |
| **Feed Management** | Feed types, inventory, feeding logs |
| **Growth Monitoring** | Weight sampling, mortality tracking |
| **Harvest** | Scheduling, records, yield tracking |
| **Sales** | Customers, orders, payments |
| **Analytics** | Dashboard, forecasts, reports |


## 🛠️ Tech Stack

- **Framework:** Django 6, Django REST Framework
- **Auth:** JWT (SimpleJWT)
- **Database:** SQLite (dev)

## 📡 API Endpoints

- `/api/auth/` - Authentication
- `/api/ponds/` - Ponds & Farms
- `/api/fish/` - Fish & Species
- `/api/feed/` - Feed Management
- `/api/growth/` - Growth Monitoring
- `/api/harvest/` - Harvest
- `/api/sales/` - Sales
- `/api/analytics/` - Analytics & Dashboard
