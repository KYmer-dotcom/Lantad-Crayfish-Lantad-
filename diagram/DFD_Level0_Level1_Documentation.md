# Aquaculture Value Chain Management System with Predictive Analytics
## Data Flow Diagram (DFD) Architectural Documentation: Level 0 & Level 1

---

## 1. Overview & System Boundary

The **Aquaculture Value Chain Management System with Predictive Analytics** is an integrated operational, sales, logistics, and predictive management platform developed for **Silay Superworm & Crayfish** (located in Brgy. Lantad, Silay City, Negros Occidental).

The system automates the end-to-end value chain across:
1. **Aquaculture Operations & Cultivation Monitoring**: Managing ponds, superworm cabins, stock batches, daily feeding, and scheduled harvesting.
2. **E-Commerce & Sales Management**: Customer ordering, automated pricing, order approvals, and invoice generation.
3. **Logistics & Dispatch Tracking**: Real-time delivery assignment, GPS routing, rider proof-of-delivery, and COD reconciliation.
4. **Predictive Analytics & Executive Reporting**: Sales forecasting, harvest yield predictions, and inventory replenishment clustering.

---

## 2. Key Corrections & Architectural Alignment

Based on the actual operational business model and Django backend architecture, the following corrections have been formalized:

| # | Item in Original Draft | Corrected Architecture | Rationale & Impact |
| :- | :--- | :--- | :--- |
| **1** | **Role: Manager** | **Role: Owner** | The business operates under a single farm owner/administrator who manages all ponds, approves orders, reviews financial reports, and inspects analytics. There are no intermediary managers. |
| **2** | **Title: "Acquaculture"** | **Title: "Aquaculture"** | Standardized correct academic spelling across all diagram headers, metadata, and reports. |
| **3** | **Data Store Integration** | **Django ORM Sync** | Data stores D1–D6 map directly to underlying database entities (`SALES_SALESORDER`, `SALES_CUSTOMER`, `OPERATIONS_POND`, `STOCK_STOCKBATCH`, `SALES_DELIVERY`, etc.). |
| **4** | **Flow Balancing** | **Level 0 $\leftrightarrow$ Level 1 Parity** | Composite data flows in the Context Diagram decompose cleanly into atomic transactional flows across processes 1.0 to 7.0 without orphan inputs or outputs. |

---

## 3. Level 0: Context Diagram Specification

The Context Diagram defines the external boundaries of the system, identifying all external entities interacting with the primary system bubble (**Process 0**).

```
                      +-------------------------------------------------------------+
                      |   Customer info, Order Details, Delivery option, Payment    |
                      |                         method                              |
                      | ----------------------------------------------------------> |
+------------------+  |                                                             |  +------------------+
|                  |  |                                                             |  |                  |
|     CUSTOMER     |  |                         PROCESS 0                           |  |      OWNER       |
|                  |  |         Aquaculture Value Chain Management System           |  |                  |
|                  |  |                 With Predictive Analytics                   |  |                  |
+------------------+  |                                                             |  +------------------+
                      | <---------------------------------------------------------- |
                      |    Order confirmation, Product Availability, Order tracking,|
                      |                        Billing receipt                      |
                      +------------------------------+------------------------------+
                                                     |
                                   Delivery          |  Delivery status,
                                  assignment,        | Completion confirm,
                                   Route map,        |  Location update
                                Customer delivery    |
                                                     v
                                            +------------------+
                                            |      RIDER       |
                                            +------------------+
```

### 3.1 External Entities
1. **Customer**: Buyers purchasing crayfish, superworms, and value-added aquaculture products via retail or wholesale.
2. **Owner**: The primary farm owner and system administrator responsible for approving orders, monitoring farm production, recording expenses, and reviewing forecasts.
3. **Rider**: Delivery personnel handling logistics, route navigation, order drop-offs, and cash collection (COD).

### 3.2 Context Data Flow Matrix

| Entity | Direction | Data Flow Name | Contained Data Elements |
| :--- | :---: | :--- | :--- |
| **Customer** | **Inflow** $\rightarrow$ System | `Customer info, Order Details, Delivery option, Payment method` | Name, contact number, delivery GPS address, selected product IDs, order quantity (kg/pcs), fulfillment type (Pickup/Delivery), payment method (GCash/COD). |
| **Customer** | **Outflow** $\leftarrow$ System | `Order confirmation, Product Availability, Order tracking, Billing receipt` | Order number, itemized invoice, total price, stock availability status, live rider GPS tracking, completion receipts. |
| **Owner** | **Inflow** $\rightarrow$ System | `Pond & feed data, Stock updates, Harvest schedule, Expense records` | Pond dimensions, water quality parameters, batch stocking quantities, daily feed weights, planned harvest dates, utility/feed expense receipts. |
| **Owner** | **Outflow** $\leftarrow$ System | `Status report, Sales summary, Sales forecast, Low stock alert` | Daily/monthly sales summaries, pond mortality rates, biomass growth curves, demand forecasts, low-stock warnings. |
| **Rider** | **Inflow** $\rightarrow$ System | `Delivery status, Completion confirm, Location update` | Acceptance/rejection of dispatch, live GPS coordinates, order status updates (`In Transit`, `Delivered`), digital proof-of-delivery (photo/signature). |
| **Rider** | **Outflow** $\leftarrow$ System | `Delivery assignment, Route map, Customer delivery` | Dispatch ticket, recipient name, contact details, destination map coordinates, packages and quantity (kg). |

---

## 4. Level 1: Data Flow Diagram (DFD) Decomposition

Level 1 breaks down Process 0 into **seven (7) core operational processes** supported by **six (6) persistent data stores**.

```
====================================================================================================
EXTERNAL ENTITIES              CORE PROCESSES (Gane & Sarson)                 DATA STORES
====================================================================================================
[ Customer ]  <=======>  ( 1.0 Browse and select )          <=======>  [ D1: Order ]
                         ( 2.0 Order management )           <=======>  [ D2: Customer ]
                         ( 3.0 Payment & Set location )     <=======>  [ D3: Production ]
[ Rider ]     <=======>  ( 4.0 Delivery dispatch )          <=======>  [ D4: Expense ]
                         ( 5.0 Management )                 <=======>  [ D5: Payment ]
[ Owner ]     <=======>  ( 6.0 Report and Monitoring )      <=======>  [ D6: Delivery ]
                         ( 7.0 Predictive Analytics )
====================================================================================================
```

### 4.1 Data Stores Mapping

| Store ID | Store Name | Associated Django Models | Stored Data Attributes |
| :---: | :--- | :--- | :--- |
| **D1** | **Order** | `sales.SalesOrder`, `sales.InventoryTransaction` | `order_number`, `order_date`, `quantity_kg`, `price_per_kg`, `total_amount`, `status`, `payment_status`. |
| **D2** | **Customer** | `sales.Customer`, `accounts.User` | `name`, `customer_type`, `phone`, `email`, `address`, `map_latitude`, `map_longitude`, `credit_limit`. |
| **D3** | **Production** | `operations.Pond`, `stock.Species`, `stock.StockBatch`, `harvest.HarvestRecord` | `pond_name`, `species_name`, `batch_code`, `current_quantity`, `current_avg_weight`, `available_stock_kg`. |
| **D4** | **Expense** | `feed.FeedType`, `feed.FeedingLog`, `sales.InputLog` | `feed_type`, `feeding_cost`, `operational_expenses`, `substrate_replenishment`, `audit_logs`. |
| **D5** | **Payment** | `sales.PaymentSetting`, `sales.SalesOrder` | `payment_method` (GCash/COD), `receipt_image`, `payment_status`, `transaction_reference`. |
| **D6** | **Delivery** | `sales.Delivery`, `sales.Rider` | `rider_id`, `scheduled_date`, `delivered_date`, `delivery_location`, `status`, `proof_of_delivery`. |

---

### 4.2 Comprehensive Level 1 Process & Data Flow Matrix

#### Process 1.0: Browse and Select
*Enables customers to query real-time catalog items, check batch stock availability, and initiate item selections.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_cust_1` | `Customer` | `1.0 Browse and select` | `Selected Product` | Product category, package type, and requested quantity. |
| `e_1_cust` | `1.0 Browse and select` | `Customer` | `Product list` | Active catalog of superworms, crayfish, and current unit prices. |
| `e_1_2` | `1.0 Browse and select` | `2.0 Order management` | `Select product` | Handover of selected items and specifications to the checkout engine. |
| `e_d3_1` | `D3 Production` | `1.0 Browse and select` | `Available stock` | Real-time harvestable stock biomass querying. |
| `e_d1_1` | `D1 Order` | `1.0 Browse and select` | `Order info` | Existing active/pending customer orders lookup. |
| `e_1_d1` | `1.0 Browse and select` | `D1 Order` | `Order info` | Temporary cart and selection reservation state. |

---

#### Process 2.0: Order Management
*Handles cart submission, sales order generation, stock reservation, and Owner approval.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_cust_2` | `Customer` | `2.0 Order management` | `Order request/details` | Finalized order items, buyer contact, and special fulfillment notes. |
| `e_2_cust` | `2.0 Order management` | `Customer` | `Order confirmation` | Generated sales order number and confirmation notice. |
| `e_owner_2`| `Owner` | `2.0 Order management` | `Order approval` | Owner verification and authorization for order processing. |
| `e_2_d1` | `2.0 Order management` | `D1 Order` | `Order records` | Creation of permanent `SalesOrder` record with `PENDING/CONFIRMED` status. |
| `e_d2_2` | `D2 Customer` | `2.0 Order management` | `Customer/order info` | Existing customer credit limits, past history, and profile details. |
| `e_2_d2` | `2.0 Order management` | `D2 Customer` | *(Customer update)* | Updates customer total purchase volume and activity metrics. |
| `e_2_3` | `2.0 Order management` | `3.0 Payment & Set location` | `Order info` | Confirmed order balance and order items passed to billing & logistics. |

---

#### Process 3.0: Payment & Set Location
*Processes payment verification (GCash transfer receipt or COD), maps delivery destination coordinates, and prepares dispatch records.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_cust_3a`| `Customer` | `3.0 Payment & Set location` | `Delivery/pickup address` | Pinpointed delivery coordinates or farm pickup preference. |
| `e_cust_3b`| `Customer` | `3.0 Payment & Set location` | `Payment details` | Uploaded GCash proof-of-payment or COD payment selection. |
| `e_3_custa`| `3.0 Payment & Set location` | `Customer` | `Payment status` | Real-time payment verification notice (`PAID` or `UNPAID`). |
| `e_3_custb`| `3.0 Payment & Set location` | `Customer` | `Payment verification (GCash/COD)` | Official digital billing invoice and payment confirmation receipt. |
| `e_rider_3`| `Rider` | `3.0 Payment & Set location` | `Cash collected (COD payment)` | Remitted cash payment collected upon physical delivery. |
| `e_3_d5` | `3.0 Payment & Set location` | `D5 Payment` | `Payment data` | Logging transaction payment verification and receipt files. |
| `e_3_d6` | `3.0 Payment & Set location` | `D6 Delivery` | `Assigned location` | Delivery geofence and destination waypoint registration. |
| `e_3_d1` | `3.0 Payment & Set location` | `D1 Order` | `Order details/Order record` | Updating order status to `PROCESSING` with cleared payment. |
| `e_3_4` | `3.0 Payment & Set location` | `4.0 Delivery dispatch` | `Order & location details` | Dispatch requisition sent to logistics dispatch engine. |

---

#### Process 4.0: Delivery Dispatch
*Assigns available riders, transmits route waypoints, monitors delivery completion, and executes automated inventory stock deductions.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_4_cust1`| `4.0 Delivery dispatch` | `Customer` | `Real-time tracking` | Live delivery progress and rider location notifications. |
| `e_4_cust2`| `4.0 Delivery dispatch` | `Customer` | `Delivery status/Completion update` | Delivery arrival and order completion alert. |
| `e_4_rider`| `4.0 Delivery dispatch` | `Rider` | `Delivery assignment & route map` | Dispatch assignment, optimal route map, and customer contact. |
| `e_rider_4`| `Rider` | `4.0 Delivery dispatch` | `Delivery status update` | Status transitions (`In Transit`, `Delivered`) and photo POD. |
| `e_4_d1` | `4.0 Delivery dispatch` | `D1 Order` | `Order status update` | Transitions order state to `DELIVERED` / `COMPLETED`. |
| `e_4_d3` | `4.0 Delivery dispatch` | `D3 Production` | `Stock deduction` | Deducts product stock balance (`quantity_kg`) via `InventoryTransaction`. |
| `e_4_d2` | `4.0 Delivery dispatch` | `D2 Customer` | `Order status update` | Increments customer successful fulfillment count. |
| `e_4_d6` | `4.0 Delivery dispatch` | `D6 Delivery` | `Dispatch records` | Saves completed delivery logs, drop-off timestamp, and driver record. |
| `e_4_5` | `4.0 Delivery dispatch` | `5.0 Management` | `Confirmed order` | Confirmed fulfillment passed to management ledger. |

---

#### Process 5.0: Management
*Central operations hub for feed recording, pond replenishment, harvest schedule tracking, and expense administration.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_owner_5a`| `Owner` | `5.0 Management` | `Approved expense entries` | Owner input for operational expenses, feed purchases, and supplies. |
| `e_owner_5b`| `Owner` | `5.0 Management` | `Stock/replenishment updates`| New species stocking, pond transfers, and harvest schedule entries. |
| `e_d6_5` | `D6 Delivery` | `5.0 Management` | `Delivery records` | Aggregated delivery efficiency, driver performance, and completion rates. |
| `e_d5_5` | `D5 Payment` | `5.0 Management` | `Payment data` | Revenue totals and payment reconciliation records. |
| `e_d3_5` | `D3 Production` | `5.0 Management` | `Production data & stock replenishment` | Current pond biomass, growth metrics, and stock availability. |
| `e_d4_5` | `D4 Expense` | `5.0 Management` | `Approved expense entries/Expense data` | Feed usage costs, labor, and farm overhead entries. |
| `e_5_6` | `5.0 Management` | `6.0 Report and Monitoring` | `Delivery data` | Consolidated operational metrics forwarded to reporting module. |

---

#### Process 6.0: Report and Monitoring
*Aggregates real-time business performance, inventory velocity, and financial health into executive dashboards for the Owner.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_owner_6`| `Owner` | `6.0 Report and Monitoring` | `Request report` | Owner query filters (date ranges, product categories, ponds). |
| `e_d3_6` | `D3 Production` | `6.0 Report and Monitoring` | `Inventory data` | Stock availability, batch mortality, and grading distribution. |
| `e_d6_6` | `D6 Delivery` | `6.0 Report and Monitoring` | `Dispatch record` | Historical delivery turnaround times and fulfillment success. |
| `e_6_owner`| `6.0 Report and Monitoring` | `Owner` | `Sales/inventory/expense summary`| Comprehensive financial, sales, inventory, and expense reports. |
| `e_6_7` | `6.0 Report and Monitoring` | `7.0 Predictive Analytics` | `Summarized data` | Time-series historical data supplied to predictive models. |

---

#### Process 7.0: Predictive Analytics
*Applies Linear Regression and Moving Average machine learning algorithms to forecast harvest maturity dates, yield volumes, and customer demand.*

| Flow ID | Source | Target | Data Flow Label | Description |
| :--- | :--- | :--- | :--- | :--- |
| `e_7_6` | `7.0 Predictive Analytics` | `6.0 Report and Monitoring` | *(Forecast integration)* | Feeds predictive forecast trends into monitoring dashboards. |
| `e_7_owner`| `7.0 Predictive Analytics` | `Owner` | `Forecast & clustering report` | Predictive harvest timelines, sales demand projections, and confidence intervals. |

---

## 5. Artifact Directory & File Sitemap

All editable diagram source files and publication-grade render assets are maintained in the repository:

- **Level 0 (Context Diagram)**:
  - Editable Draw.io: [`diagram/Level_0_Context_Diagram.drawio`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/Level_0_Context_Diagram.drawio)
  - Standalone XML: [`diagram/Level_0_Context_Diagram.xml`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/Level_0_Context_Diagram.xml)
  - 3x PNG High-Res: [`diagram/Level_0_Context_Diagram.png`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/Level_0_Context_Diagram.png)
- **Level 1 (Data Flow Diagram)**:
  - Editable Draw.io: [`diagram/Level_1_DFD.drawio`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/Level_1_DFD.drawio)
  - Standalone XML: [`diagram/Level_1_DFD.xml`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/Level_1_DFD.xml)
  - 3x PNG High-Res: [`diagram/Level_1_DFD.png`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/Level_1_DFD.png)
- **Entity-Relationship Diagram (ERD)**:
  - Editable Draw.io: [`diagram/ERD_Diagram.drawio`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/ERD_Diagram.drawio)
  - Standalone XML: [`diagram/ERD_Diagram.xml`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/ERD_Diagram.xml)
  - 3x PNG High-Res: [`diagram/ERD_Diagram.png`](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/ERD_Diagram.png)
