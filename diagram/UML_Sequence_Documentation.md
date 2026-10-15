# UML Sequence Diagram Documentation
**Aquaculture Value Chain Management System with Predictive Analytics**  
*Silay Superworm & Crayfish, Brgy. Lantad, Silay City, Negros Occidental*

---

## 1. Overview
The **UML Sequence Diagram** illustrates the chronological interaction, message exchanges, and data synchronization among system entities during an end-to-end commercial transaction lifecycle—spanning catalog browsing, order checkout, GCash/COD payment verification, courier dispatching, and Proof of Delivery (POD) completion.

- **Diagram Files**:
  - Draw.io Diagram: [UML_Sequence_Diagram.drawio](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/UML_Sequence_Diagram.drawio)
  - XML Source: [UML_Sequence_Diagram.xml](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/UML_Sequence_Diagram.xml)
  - High-Resolution PNG: [UML_Sequence_Diagram.png](file:///c:/Users/kymer/Desktop/Lantad%20ACarwfish%20Django/diagram/UML_Sequence_Diagram.png)

---

## 2. Participants / Lifelines

| Lifeline / Participant | Stereotype / Type | Description |
| :--- | :--- | :--- |
| **Customer** | `Actor` | External buyer placing orders, selecting payment options, and tracking live fulfillment. |
| **Web App / UI** | `Boundary / View` | Responsive frontend interface handling user input, form validations, and interactive maps. |
| **Django Server** | `Controller / Service` | Backend business logic, API endpoints, role-based authorization, and dispatch coordinator. |
| **Database** | `Entity / Data Store` | Relational database (PostgreSQL/SQLite) managing orders, inventory, payments, and dispatches. |
| **Farm Owner** | `Actor / Administrator` | Enterprise manager verifying payments, approving orders, and assigning couriers. |
| **Delivery Rider** | `Actor / Courier` | Logistics driver receiving route waypoints, updating in-transit status, and submitting POD. |

---

## 3. Transaction Workflow Phases

### Phase 1: Catalog Browsing & Cart Checkout
1. **Customer $\rightarrow$ Web App**: Browses product catalog and selects aquaculture items (live redclaw crayfish, packaged superworms, specialized feeds).
2. **Web App $\rightarrow$ Django Server**: `GET /api/products/` to fetch real-time inventory counts and dual pricing (per piece / per kg).
3. **Django Server $\rightarrow$ Database**: Queries active inventory tables and batch stock levels.
4. **Database $\rightarrow$ Django Server**: Returns stock availability and current unit prices.
5. **Django Server $\rightarrow$ Web App**: Renders product catalog cards and dynamic cart totals.
6. **Customer $\rightarrow$ Web App**: Selects fulfillment option (Delivery / Pickup), enters delivery address, and submits checkout.
7. **Web App $\rightarrow$ Django Server**: `POST /checkout/` with order line items and customer destination details.
8. **Django Server $\rightarrow$ Database**: Inserts new Order record (status: `PENDING`) and creates soft stock reservation.
9. **Database $\rightarrow$ Django Server**: Confirms order record creation and returns Order `#ID`.

### Phase 2: Payment Settlement & Owner Verification
10. **Customer $\rightarrow$ Web App**: Selects GCash (uploads reference receipt) or Cash on Delivery (COD).
11. **Web App $\rightarrow$ Django Server**: `POST /payment/submit/` with payment details and receipt attachment.
12. **Django Server $\rightarrow$ Database**: Saves Payment transaction record (status: `UNVERIFIED` for GCash or `COD`).
13. **Django Server $\rightarrow$ Farm Owner**: Dispatches high-priority alert for pending order and payment review.
14. **Farm Owner $\rightarrow$ Web App**: Accesses admin verification screen, inspects receipt, and clicks *Approve*.
15. **Web App $\rightarrow$ Django Server**: `POST /order/approve/` with `order_id`.
16. **Django Server $\rightarrow$ Database**: Commits database update setting `Order.status = CONFIRMED` and `Payment.status = APPROVED`.

### Phase 3: Courier Dispatch & Live Transit Tracking
17. **Farm Owner $\rightarrow$ Web App**: Views unassigned confirmed orders and available delivery couriers.
18. **Farm Owner $\rightarrow$ Web App**: Selects active Delivery Rider and clicks *Assign Dispatch*.
19. **Web App $\rightarrow$ Django Server**: `POST /dispatch/assign/` with `(rider_id, order_id)`.
20. **Django Server $\rightarrow$ Database**: Creates Dispatch record, locks rider assignment, and logs OpenStreetMap route waypoints.
21. **Django Server $\rightarrow$ Delivery Rider**: Pushes dispatch alert with customer phone, drop-off coordinates, and optimized map.
22. **Delivery Rider $\rightarrow$ Django Server**: `POST /delivery/transit/` marking order status `IN_TRANSIT`.
23. **Django Server $\rightarrow$ Customer**: Pushes live transit notification, route visualization, and estimated time of arrival (ETA).

### Phase 4: Delivery Handover, POD & Analytics Commitment
24. **Delivery Rider $\rightarrow$ Customer**: Delivers physical package and collects COD cash payment (if applicable).
25. **Delivery Rider $\rightarrow$ Web App**: Captures Proof of Delivery (POD) photo/signature and marks order `DELIVERED`.
26. **Web App $\rightarrow$ Django Server**: `POST /delivery/complete/` with POD payload and delivery timestamp.
27. **Django Server $\rightarrow$ Database**: Commits hard inventory deduction from production batch and sets `Order.status = COMPLETED`.
28. **Django Server $\rightarrow$ Database**: Logs finalized sales revenue and updates transaction audit logs.
29. **Django Server $\rightarrow$ Customer**: Dispatches official electronic invoice and delivery confirmation receipt.
30. **Django Server $\rightarrow$ Farm Owner**: Updates real-time sales dashboard, expense statements, and feeds historical revenue into Linear Regression predictive forecasting models.
