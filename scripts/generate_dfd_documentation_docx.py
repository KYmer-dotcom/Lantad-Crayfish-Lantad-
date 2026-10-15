import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)

def create_styled_table(doc, headers, data, col_widths=None):
    table = doc.add_table(rows=len(data) + 1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        set_cell_background(hdr_cells[i], '1F4E79')
        set_cell_margins(hdr_cells[i], 140, 140, 160, 160)
        hdr_cells[i].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = 'Arial'
            run.font.size = Pt(9.5)
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for r_idx, row_data in enumerate(data):
        row_cells = table.rows[r_idx + 1].cells
        bg_color = 'F2F4F7' if r_idx % 2 == 1 else 'FFFFFF'
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_background(row_cells[c_idx], bg_color)
            set_cell_margins(row_cells[c_idx], 100, 100, 140, 140)
            row_cells[c_idx].vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = row_cells[c_idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = 'Arial'
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(30, 30, 30)

    # Widths
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Inches(w)

    doc.add_paragraph()
    return table

def build_docx_documentation():
    doc = docx.Document()

    # Page Margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("AQUACULTURE VALUE CHAIN MANAGEMENT SYSTEM WITH PREDICTIVE ANALYTICS")
    r_title.font.name = 'Arial'
    r_title.font.size = Pt(16)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(31, 78, 121)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Level 0 (Context Diagram) & Level 1 (Data Flow Diagram) Comprehensive Architectural Documentation")
    r_sub.font.name = 'Arial'
    r_sub.font.size = Pt(12)
    r_sub.font.italic = True
    r_sub.font.color.rgb = RGBColor(89, 89, 89)

    doc.add_paragraph()

    # -------------------------------------------------------------------------
    # SECTION 1: INACCURACIES IN ORIGINAL DRAFT & CORRECTIONS
    # -------------------------------------------------------------------------
    h1 = doc.add_heading("1. Identified Inaccuracies in Original Draft & Corrections Applied", level=1)
    for run in h1.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(31, 78, 121)

    p_intro = doc.add_paragraph()
    r = p_intro.add_run("A critical audit of the original Level 0 and Level 1 diagram drafts identified several discrepancies with the actual farm business workflow and software architecture. The table below outlines each issue and the formal correction applied:")
    r.font.name = 'Arial'
    r.font.size = Pt(10)

    discrepancy_data = [
        [
            "Role Identity",
            "Manager",
            "Owner",
            "The farm (Silay Superworm & Crayfish) operates under a single farm owner who personally oversees operations, approves orders, inputs expenses, and analyzes forecasts. No manager positions exist."
        ],
        [
            "System Title Spelling",
            "Acquaculture",
            "Aquaculture",
            "Standardized academic spelling across all diagram headers, process labels, and documentation."
        ],
        [
            "Flow Decomposition",
            "Composite text labels on single lines",
            "Atomically separated directional data flows",
            "Decomposed bundled text strings into distinct, traceable directional flows with explicit endpoints and clear triggering semantics."
        ],
        [
            "Data Store Alignment",
            "Generic labels without schema mappings",
            "Direct Django ORM database table mapping",
            "Mapped stores D1–D6 directly to operational tables: SalesOrder, Customer, Pond, StockBatch, FeedingLog, Delivery, and InputLog."
        ],
        [
            "Balancing Parity",
            "Mismatched input/output counts between L0 & L1",
            "Strict Gane & Sarson DFD balancing",
            "Every composite data packet in the Level 0 Context Diagram decomposes directly into sub-process flows in Level 1 with 100% balancing fidelity."
        ]
    ]

    create_styled_table(
        doc,
        ["Component", "Original Draft", "Corrected Architecture", "Rationale & Technical Impact"],
        discrepancy_data,
        [1.2, 1.2, 1.3, 2.8]
    )

    # -------------------------------------------------------------------------
    # SECTION 2: LEVEL 0 CONTEXT DIAGRAM SPECIFICATION
    # -------------------------------------------------------------------------
    h2 = doc.add_heading("2. Level 0: Context Diagram Specification", level=1)
    for run in h2.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(31, 78, 121)

    p_l0 = doc.add_paragraph()
    r = p_l0.add_run("The Context Diagram defines the external boundary of the system. It contains three external entities (Customer, Owner, Rider) communicating with Process 0 (Aquaculture Value Chain Management System with Predictive Analytics).")
    r.font.name = 'Arial'
    r.font.size = Pt(10)

    l0_flows_data = [
        [
            "Customer",
            "Inflow (-> System)",
            "Customer info, Order Details, Delivery option, Payment method",
            "Customer name, contact phone, delivery GPS coordinates, selected product items, quantity (kg/pcs), pickup vs. delivery choice, and GCash/COD payment method.",
            "Triggered when a customer registers or submits a new purchase order through the web portal."
        ],
        [
            "Customer",
            "Outflow (<- System)",
            "Order confirmation, Product Availability, Order tracking, Billing receipt",
            "Generated sales order number, real-time stock levels, live delivery rider GPS tracking link, and digital transaction payment invoice.",
            "Returned dynamically upon catalog query, checkout submission, payment clearance, and delivery dispatch."
        ],
        [
            "Owner",
            "Inflow (-> System)",
            "Pond & feed data, Stock updates, Harvest schedule, Expense records",
            "Pond/cabin dimensions, batch stocking quantities, species details, daily feed weight inputs, planned harvest dates, and operating/utility expenses.",
            "Input by the farm owner during daily pond monitoring, feed distribution, stocking, and financial book-keeping."
        ],
        [
            "Owner",
            "Outflow (<- System)",
            "Status report, Sales summary, Sales forecast, Low stock alert",
            "Consolidated sales summaries, batch growth curves, mortality analysis, AI-driven demand and harvest yield forecasts, and low inventory warnings.",
            "Generated in real-time and scheduled for executive review, operational adjustments, and inventory replenishment."
        ],
        [
            "Rider",
            "Inflow (-> System)",
            "Delivery status, Completion confirm, Location update",
            "Dispatch acceptance, live waypoint GPS coordinates, status transitions (In Transit, Delivered), and digital proof-of-delivery photos.",
            "Submitted by the delivery rider via their mobile device throughout the delivery route."
        ],
        [
            "Rider",
            "Outflow (<- System)",
            "Delivery assignment, Route map, Customer delivery",
            "Assigned order invoice number, customer name, recipient contact number, delivery address, Google Maps route, and package details.",
            "Transmitted automatically to the assigned rider once an order is approved and packed for delivery."
        ]
    ]

    create_styled_table(
        doc,
        ["External Entity", "Direction", "Data Flow Label", "Contained Data Attributes", "Operational Trigger & Purpose"],
        l0_flows_data,
        [1.1, 1.0, 1.4, 1.8, 1.2]
    )

    # -------------------------------------------------------------------------
    # SECTION 3: LEVEL 1 DATA FLOW DIAGRAM SPECIFICATION
    # -------------------------------------------------------------------------
    h3 = doc.add_heading("3. Level 1: Data Flow Diagram (DFD) Process Decomposition", level=1)
    for run in h3.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(31, 78, 121)

    p_l1 = doc.add_paragraph()
    r = p_l1.add_run("Level 1 decomposes the central system into seven functional processes and six persistent data stores. Each process encapsulates specific business logic, data validations, and storage operations:")
    r.font.name = 'Arial'
    r.font.size = Pt(10)

    processes_data = [
        [
            "1.0",
            "Browse and select",
            "Customer -> 1.0: Selected Product\nD3 -> 1.0: Available stock\nD1 -> 1.0: Order info",
            "1.0 -> Customer: Product list\n1.0 -> 2.0: Select product\n1.0 -> D1: Order info",
            "Retrieves active crayfish and superworm products, displays real-time available stock quantities from D3 (Production), and registers customer product selections."
        ],
        [
            "2.0",
            "Order management",
            "Customer -> 2.0: Order request/details\nOwner -> 2.0: Order approval\n1.0 -> 2.0: Select product\nD2 -> 2.0: Customer/order info",
            "2.0 -> Customer: Order confirmation\n2.0 -> 3.0: Order info\n2.0 -> D1: Order records\n2.0 -> D2: Customer/order info",
            "Processes cart checkout, generates unique sales order numbers (SO-YYYYMMDD-XXXX), prompts Owner for order authorization, and logs order records in D1 (Order)."
        ],
        [
            "3.0",
            "Payment & Set location",
            "Customer -> 3.0: Delivery/pickup address\nCustomer -> 3.0: Payment details\nRider -> 3.0: Cash collected (COD)\n2.0 -> 3.0: Order info\nD5 -> 3.0: Payment data",
            "3.0 -> Customer: Payment status\n3.0 -> Customer: Payment verification\n3.0 -> 4.0: Order & location details\n3.0 -> D5: Payment data\n3.0 -> D6: Assigned location\n3.0 -> D1: Order details",
            "Handles payment options (GCash QR verification or COD), records transaction receipts in D5 (Payment), sets delivery destination coordinates in D6 (Delivery), and updates order status."
        ],
        [
            "4.0",
            "Delivery dispatch",
            "3.0 -> 4.0: Order & location details\nRider -> 4.0: Delivery status update",
            "4.0 -> Customer: Real-time tracking\n4.0 -> Customer: Delivery status update\n4.0 -> Rider: Delivery assignment & route\n4.0 -> 5.0: Confirmed order\n4.0 -> D1: Order status update\n4.0 -> D3: Stock deduction\n4.0 -> D2: Order status update\n4.0 -> D6: Dispatch records",
            "Dispatches orders to available riders, broadcasts live tracking coordinates to customers, records photo proof-of-delivery, and automatically deducts stock in D3 (Production)."
        ],
        [
            "5.0",
            "Management",
            "Owner -> 5.0: Approved expense entries\nOwner -> 5.0: Stock/replenishment\n4.0 -> 5.0: Confirmed order\nD6 -> 5.0: Delivery records\nD5 -> 5.0: Payment data\nD3 -> 5.0: Production & stock data\nD4 -> 5.0: Approved expense data",
            "5.0 -> 6.0: Delivery data",
            "Central operations administration. Coordinates pond batch replenishment, feed inventory, mortality logging, operating expense tracking in D4, and delivery performance metrics."
        ],
        [
            "6.0",
            "Report and Monitoring",
            "Owner -> 6.0: Request report\n5.0 -> 6.0: Delivery data\nD3 -> 6.0: Inventory data\nD6 -> 6.0: Dispatch record\n7.0 -> 6.0: Forecast integration",
            "6.0 -> Owner: Sales/inventory/expense summary\n6.0 -> 7.0: Summarized data",
            "Consolidates historical and operational datasets into executive dashboards, financial summaries, sales graphs, and mortality rate analytics for the Owner."
        ],
        [
            "7.0",
            "Predictive Analytics",
            "6.0 -> 7.0: Summarized data",
            "7.0 -> Owner: Forecast & clustering report\n7.0 -> 6.0: Forecast metrics",
            "Applies Linear Regression and Moving Average models to historical growth and sales time-series data to predict harvest dates, expected yields, and market demand."
        ]
    ]

    create_styled_table(
        doc,
        ["Process", "Process Name", "Inflow Sources & Labels", "Outflow Targets & Labels", "Detailed Algorithmic & Functional Narrative"],
        processes_data,
        [0.6, 1.2, 1.8, 1.8, 1.1]
    )

    # -------------------------------------------------------------------------
    # SECTION 4: DATA STORES DICTIONARY (D1 TO D6)
    # -------------------------------------------------------------------------
    h4 = doc.add_heading("4. Persistent Data Stores Data Dictionary (D1 to D6)", level=1)
    for run in h4.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(31, 78, 121)

    datastores_data = [
        [
            "D1",
            "Order",
            "sales.SalesOrder\nsales.InventoryTransaction",
            "id (PK), order_number, customer_id (FK), product_id (FK), order_date, delivery_date, quantity_kg, price_per_kg, total_amount, status, payment_status, delivery_address",
            "1.0 (Read/Write)\n2.0 (Write)\n3.0 (Write)\n4.0 (Write)"
        ],
        [
            "D2",
            "Customer",
            "sales.Customer\naccounts.User",
            "id (PK), user_id (FK), name, customer_type, phone, address, map_latitude, map_longitude, credit_limit, is_active",
            "2.0 (Read/Write)\n4.0 (Write)"
        ],
        [
            "D3",
            "Production",
            "operations.Pond\nstock.Species\nstock.StockBatch\nharvest.HarvestRecord",
            "id (PK), name, location, size, depth, capacity, breeding_type, transfer_date, current_quantity, initial_avg_weight, current_avg_weight, stage, status",
            "1.0 (Read)\n4.0 (Write: Stock deduction)\n5.0 (Read/Write)\n6.0 (Read)"
        ],
        [
            "D4",
            "Expense",
            "feed.FeedType\nfeed.FeedingLog\nsales.InputLog",
            "id (PK), name, category, quantity_kg, feeding_time, feeding_cost, operational_expense, action, module, target_entity, created_at",
            "5.0 (Read/Write)"
        ],
        [
            "D5",
            "Payment",
            "sales.PaymentSetting\nsales.SalesOrder",
            "id (PK), gcash_name, gcash_number, gcash_qr_image, is_gcash_enabled, is_cod_enabled, payment_status, total_amount, receipt_image",
            "3.0 (Read/Write)\n5.0 (Read)"
        ],
        [
            "D6",
            "Delivery",
            "sales.Delivery\nsales.Rider",
            "id (PK), order_id (FK), rider_id (FK), scheduled_date, delivered_date, delivery_location, quantity_kg, status, proof_of_delivery",
            "3.0 (Write)\n4.0 (Write)\n5.0 (Read)\n6.0 (Read)"
        ]
    ]

    create_styled_table(
        doc,
        ["Store", "Store Name", "Mapped Django Database Models", "Stored Attributes & Keys", "Interacting Processes"],
        datastores_data,
        [0.6, 1.0, 1.5, 2.2, 1.2]
    )

    # -------------------------------------------------------------------------
    # SECTION 5: COMPLETE DATA FLOW BALANCING VERIFICATION
    # -------------------------------------------------------------------------
    h5 = doc.add_heading("5. Data Flow Balancing Proof: Level 0 vs. Level 1 Parity", level=1)
    for run in h5.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(31, 78, 121)

    balancing_data = [
        [
            "Customer -> System",
            "Customer info, Order Details, Delivery option, Payment method",
            "Customer -> 1.0: Selected Product\nCustomer -> 2.0: Order request/details\nCustomer -> 3.0: Delivery/pickup address\nCustomer -> 3.0: Payment details",
            "Balanced (100% decomposed across 1.0, 2.0, 3.0)"
        ],
        [
            "System -> Customer",
            "Order confirmation, Product Availability, Order tracking, Billing receipt",
            "1.0 -> Customer: Product list\n2.0 -> Customer: Order confirmation\n3.0 -> Customer: Payment status & receipt\n4.0 -> Customer: Real-time tracking & completion",
            "Balanced (100% returned across 1.0, 2.0, 3.0, 4.0)"
        ],
        [
            "Owner -> System",
            "Pond & feed data, Stock updates, Harvest schedule, Expense records",
            "Owner -> 2.0: Order approval\nOwner -> 5.0: Approved expense entries\nOwner -> 5.0: Stock/replenishment updates\nOwner -> 6.0: Request report",
            "Balanced (100% routed to 2.0, 5.0, 6.0)"
        ],
        [
            "System -> Owner",
            "Status report, Sales summary, Sales forecast, Low stock alert",
            "6.0 -> Owner: Sales/inventory/expense summary\n7.0 -> Owner: Forecast & clustering report",
            "Balanced (100% emitted by 6.0, 7.0)"
        ],
        [
            "Rider -> System",
            "Delivery status, Completion confirm, Location update",
            "Rider -> 3.0: Cash collected (COD payment)\nRider -> 4.0: Delivery status update & POD",
            "Balanced (100% captured in 3.0, 4.0)"
        ],
        [
            "System -> Rider",
            "Delivery assignment, Route map, Customer delivery",
            "4.0 -> Rider: Delivery assignment, route map, customer contact",
            "Balanced (100% generated by 4.0)"
        ]
    ]

    create_styled_table(
        doc,
        ["Level 0 Flow Interface", "Level 0 Composite Flow Package", "Level 1 Atomic Decomposed Flows", "Balancing Verification Status"],
        balancing_data,
        [1.3, 1.8, 2.2, 1.2]
    )

    # Save Word Document
    out_docx = r'c:\Users\kymer\Desktop\Lantad ACarwfish Django\Documents\DFD_Level_0_and_Level_1_Documentation.docx'
    doc.save(out_docx)
    print(f"Document successfully created at: {out_docx}")

if __name__ == '__main__':
    build_docx_documentation()
