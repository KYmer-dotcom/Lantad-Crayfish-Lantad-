# UML Use Case Diagram Documentation
**Aquaculture Value Chain Management System with Predictive Analytics**  
*Silay Superworm & Crayfish, Brgy. Lantad, Silay City, Negros Occidental*

---

## 1. Overview
The **UML Use Case Diagram** defines the functional boundaries of the *Aquaculture Value Chain Management System with Predictive Analytics*, depicting interactions between external user roles (Actors) and the high-level system services (Use Cases).

- **System Boundary**: `Aquaculture Value Chain Management System with Predictive Analytics`
- **Primary Actors**: **Customer**, **Delivery Rider**, and **Farm Owner (Administrator)**
- **Diagram Files**:
  - Draw.io Diagram: [UML_Use_Case_Diagram.drawio](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/UML_Use_Case_Diagram.drawio)
  - XML Source: [UML_Use_Case_Diagram.xml](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/UML_Use_Case_Diagram.xml)
  - High-Resolution PNG: [UML_Use_Case_Diagram.png](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/UML_Use_Case_Diagram.png)

---

## 2. Actors Specification

| Actor | Role Type | Description & Operational Scope |
| :--- | :--- | :--- |
| **Customer** | Primary External User | Commercial buyers and retail customers who browse available aquaculture stock (live crayfish, packaged superworms, feed, organic fertilizer), manage shopping carts, place orders, upload GCash proofs/choose COD, and track live order deliveries. |
| **Delivery Rider** | Primary Internal User | Couriers responsible for managing assigned delivery orders, viewing optimized routing maps, providing real-time transit status updates, capturing Proof of Delivery (POD) confirmations, and settling COD collections. |
| **Farm Owner (Administrator)** | System Controller & Primary Stakeholder | Enterprise administrator who manages aquaculture pond life cycles (water quality, feeding, mortality, harvest batches), regulates commercial inventory and dual pricing (per piece / per kg), logs operational expenses, approves orders/payments, dispatches couriers, generates executive financial reports, and reviews predictive analytics forecasts. |

---

## 3. Use Case Specifications

| Use Case ID | Use Case Name | Primary Actors | Description | Stereotype / Dependencies |
| :--- | :--- | :--- | :--- | :--- |
| **UC1** | Authenticate & Manage Profile | Customer, Rider, Owner | Secure login, session management, role routing, and customer profile phone registration. | Core Shared Service |
| **UC2** | Browse Product Catalog & Filter Stock | Customer | Browse commercial product catalog, filter by category (Crayfish, Superworms, Feeds, Fertilizers), and verify real-time inventory availability. | - |
| **UC3** | Place Order & Manage Shopping Cart | Customer | Add items to cart, select quantity/pricing tier (per-piece or per-kg), input delivery/pickup address, and place order requests. | `<<include>>` UC4 (Process Payment) |
| **UC4** | Process Payment (GCash / COD Settlement) | Customer, Owner, Rider | Select payment gateway (GCash receipt upload or COD), settle transactions, and verify payment approvals. | - |
| **UC5** | Track Order Status & Delivery Route Map | Customer, Rider | Real-time tracking of order fulfillment lifecycle (Pending, Confirmed, Dispatched, In Transit, Delivered) with OpenStreetMap route visualization. | - |
| **UC6** | Manage Courier Dispatch & View Delivery Orders | Rider, Owner | Owner assigns dispatch orders to active couriers; riders view assigned deliveries, customer destination coordinates, and route waypoints. | `<<include>>` UC7 (Submit Proof of Delivery) |
| **UC7** | Submit Proof of Delivery (POD & Status Update) | Rider | Courier captures recipient signature/confirmation and updates final delivery status to mark order completed. | - |
| **UC8** | Manage Farm Operations (Ponds, Feeding, Harvest) | Owner | Record pond parameters, feeding schedules, mortality logs, growth stage transitions, and batch harvest records. | - |
| **UC9** | Manage Inventory & Dual Pricing (pc/kg) | Owner | Monitor real-time product stock levels, adjust unit pricing, configure low-stock threshold alerts, and replenish inventory. | - |
| **UC10** | Record & Categorize Operational Expenses | Owner | Log operational expenses (feed purchases, electricity, logistics fuel, maintenance labor) with receipt attachments and category tags. | - |
| **UC11** | Generate Executive Reports & Audit Trails | Owner | Compile and export comprehensive sales summaries, expense statements, inventory balances, and system transaction audit logs. | - |
| **UC12** | View Predictive Analytics (Sales Forecast & Clustering) | Owner | Access interactive analytics dashboard with Linear Regression sales forecasts and harvest yield predictions. | `<<include>>` UC13 (K-Means Clustering) |
| **UC13** | Perform K-Means Customer Segmentation | Owner | Execute unsupervised machine learning clustering to group commercial customers by purchasing frequency, monetary value, and regional location. | - |

---

## 4. Association Matrix

```
                      +-------------------+-----------------+-----------------------+
                      |     Customer      | Delivery Rider  | Farm Owner (Admin)    |
+---------------------+-------------------+-----------------+-----------------------+
| UC1 (Auth)          |         X         |        X        |           X           |
| UC2 (Browse)        |         X         |                 |                       |
| UC3 (Place Order)   |         X         |                 |                       |
| UC4 (Payment)       |         X         |        X        |           X           |
| UC5 (Tracking)      |         X         |        X        |                       |
| UC6 (Dispatch)      |                   |        X        |           X           |
| UC7 (POD)           |                   |        X        |                       |
| UC8 (Farm Ops)      |                   |                 |           X           |
| UC9 (Inventory)     |                   |                 |           X           |
| UC10 (Expenses)     |                   |                 |           X           |
| UC11 (Reports)      |                   |                 |           X           |
| UC12 (Predictive)   |                   |                 |           X           |
| UC13 (Clustering)   |                   |                 |           X (via UC12)|
+---------------------+-------------------+-----------------+-----------------------+
```
