# Silay Superworm & Crayfish Aquaculture - Management System

A full-featured, enterprise-grade aquaculture and inventory management system built entirely with Django, Django REST Framework, and HTMX.

## 📁 Project Structure

```
Lantad ACarwfish/
└── System/                  # Django Root Project Directory
    ├── apps/                # Pluggable Django Applications
    │   ├── accounts/        # 👤 User Profiles, Roles & Auth Views
    │   ├── analytics/       # 📊 AI Forecasts, Dashboard & PDF/CSV Reports
    │   ├── fish/            # 🦞 Stock Monitoring & Species Classification
    │   ├── ponds/           # 🏞️ Operations, Farm Assets & Superworm Grids
    │   └── sales/           # 💰 Customers, Product Inventory, Orders & Deliveries
    ├── core/                # ⚙️ Django Project Settings, WSGI/ASGI & Configs
    ├── static/              # 🎨 Static Assets (CSS, JS, Product Images: Azula, Crayfish, Superworm)
    ├── templates/           # 🖥️ Django HTML Templates & HTMX Partials (App-specific & Partials)
    ├── db.sqlite3           # 🗄️ SQLite Database
    └── manage.py            # 🛠️ Django Management Script
```

## 🚀 Quick Start

### 1. Open Terminal & Navigate to Project Directory
Open PowerShell or your preferred terminal in the project root, then navigate into the `System` directory where `manage.py` resides:
```powershell
cd System
```

### 2. (Optional) Activate Virtual Environment
If you are using a virtual environment located in the root directory:
```powershell
..\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```powershell
py -3 -m pip install django djangorestframework djangorestframework-simplejwt django-cors-headers django-crispy-forms crispy-tailwind django-htmx Pillow
```
cd System
### 4. Run Database Migrations
```powershell
py -3 manage.py migrate
```

### 5. Start the Development Server
```powershell
py -3 manage.py runserver
```

Server runs locally at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔐 Navigation & Credentials

### System Access Points
- **Main Portal / Login:** [http://127.0.0.1:8000/login/](http://127.0.0.1:8000/login/)
- **Customer Portal:** [http://127.0.0.1:8000/customer/](http://127.0.0.1:8000/customer/)
- **Django Admin:** [http://127.0.0.1:8000/admin/login/](http://127.0.0.1:8000/admin/login/)

### Default Admin Account
- **Username:** `admin`
- **Password:** `admin123`
- **Role:** Owner (Full System Access)

---

## 📦 System Modules & Capabilities

| Sidebar Module / Area | Underlying App | Core Functionality |
|-----------------------|----------------|--------------------|
| **Dashboard** | `analytics` | High-level operational overview, active crayfish stock count, and revenue metrics. |
| **Stock Monitoring** | `fish` | Define aquatic species (Crayfish, Superworms) and monitor active stock batches. |
| **Operations** | `ponds` | Manage active aquaculture units, operational status, and assigned personnel. |
| **Inventory Management**| `sales` | Manage active product inventory (Azula, Breeder Crayfish, Superworms), pricing, and stock levels. |
| **Delivery** | `sales` | Track scheduled dispatches, shipments in transit, map pins, and delivery completions. |
| **Sales Management** | `sales` | Process customer sales orders, track transaction statuses, and manage payments. |
| **Reports & Analytics**| `analytics` | Generate predictive market demand forecasts and export downloadable PDF/CSV reports. |
| **User Administration**| `accounts` | Manage user profiles, system roles (Owner, Manager, Caretaker), and authentication. |
| **Notifications** | `notifications`| View real-time system alerts, low stock warnings, and operational updates. |

---

## 🛠️ Technology Stack

- **Backend Framework:** Django 6.x, Django REST Framework (DRF)
- **Frontend Architecture:** Django Templates, Vanilla CSS (Premium Dark Aquaculture Theme), HTMX Partials
- **Authentication:** Session-based Authentication & JWT (SimpleJWT)
- **Database:** SQLite3 (Development / Local Storage)